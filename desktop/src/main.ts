import './style.css'
import * as XLSX from 'xlsx'
import { convertFileSrc, invoke } from '@tauri-apps/api/core'

type ReportStatus = 'remote' | 'downloaded' | 'text' | 'analyzed'
type TaskType = 'download' | 'convert' | 'analyze' | 'export'
type TaskStatus = 'queued' | 'running' | 'done' | 'failed'

type Report = {
  id: string
  code: string
  company: string
  title: string
  year: number
  market: string
  industry: string
  status: ReportStatus
  size: string
  url: string
  pdfPath?: string
  txtPath?: string
  analysisPath?: string
}

type Company = {
  code: string
  name: string
  market: string
}

type AppTask = {
  id: string
  reportId?: string
  type: TaskType
  label: string
  status: TaskStatus
  progress: number
  error?: string
}

type AppState = {
  reports: Report[]
  selectedId: string
  query: string
  year: string
  market: string
  reportType: string
  status: string
  sourceName: string
  pdfDir: string
  outputDir: string
  tasks: AppTask[]
}

type FileResult = {
  path: string
  size: string
}

type AnalysisResult = {
  path: string
  total_chars: number
  keyword_hits: number
}

type ExportRow = {
  code: string
  company: string
  title: string
  year: number
  market: string
  industry: string
  status: string
  url: string
  pdf_path: string
  txt_path: string
  analysis_path: string
}

type AnnouncementResult = {
  code: string
  company: string
  title: string
  year: number
  market: string
  url: string
  size: string
}

const STORAGE_KEY = 'annualreport-desktop-state-v2'
const COMPANY_CACHE_KEY = 'annualreport-desktop-company-cache-v1'

const defaultState: AppState = {
  reports: [],
  selectedId: '',
  query: '',
  year: '全部',
  market: '全部板块',
  reportType: 'annual',
  status: '全部',
  sourceName: '未导入',
  pdfDir: '',
  outputDir: '',
  tasks: [],
}

const statusText: Record<ReportStatus, string> = {
  remote: '远程',
  downloaded: 'PDF',
  text: 'TXT',
  analyzed: '分析',
}

const statusFilterText: Record<ReportStatus, string> = {
  remote: '远程',
  downloaded: 'PDF',
  text: 'TXT',
  analyzed: '已分析',
}

const taskText: Record<TaskType, string> = {
  download: '下载 PDF',
  convert: '转 TXT',
  analyze: '运行分析',
  export: '导出结果',
}

const companySeed: Company[] = [
  { code: '000001', name: '平安银行', market: '深市主板' },
  { code: '000002', name: '万科A', market: '深市主板' },
  { code: '000333', name: '美的集团', market: '深市主板' },
  { code: '000651', name: '格力电器', market: '深市主板' },
  { code: '000858', name: '五粮液', market: '深市主板' },
  { code: '002415', name: '海康威视', market: '深市主板' },
  { code: '002594', name: '比亚迪', market: '深市主板' },
  { code: '300014', name: '亿纬锂能', market: '创业板' },
  { code: '300059', name: '东方财富', market: '创业板' },
  { code: '300124', name: '汇川技术', market: '创业板' },
  { code: '300274', name: '阳光电源', market: '创业板' },
  { code: '300750', name: '宁德时代', market: '创业板' },
  { code: '600000', name: '浦发银行', market: '沪市主板' },
  { code: '600030', name: '中信证券', market: '沪市主板' },
  { code: '600036', name: '招商银行', market: '沪市主板' },
  { code: '600048', name: '保利发展', market: '沪市主板' },
  { code: '600276', name: '恒瑞医药', market: '沪市主板' },
  { code: '600309', name: '万华化学', market: '沪市主板' },
  { code: '600519', name: '贵州茅台', market: '沪市主板' },
  { code: '600887', name: '伊利股份', market: '沪市主板' },
  { code: '601012', name: '隆基绿能', market: '沪市主板' },
  { code: '601318', name: '中国平安', market: '沪市主板' },
  { code: '601398', name: '工商银行', market: '沪市主板' },
  { code: '601668', name: '中国建筑', market: '沪市主板' },
  { code: '601888', name: '中国中免', market: '沪市主板' },
  { code: '603259', name: '药明康德', market: '沪市主板' },
  { code: '688012', name: '中微公司', market: '科创板' },
  { code: '688036', name: '传音控股', market: '科创板' },
  { code: '688111', name: '金山办公', market: '科创板' },
  { code: '688981', name: '中芯国际', market: '科创板' },
]

let state = loadState()
let companyCache = loadCompanyCache()
let queryRenderTimer: number | undefined
let isComposingQuery = false

const root = document.querySelector<HTMLDivElement>('#app')
if (!root) throw new Error('Missing #app root element')
const appRoot = root

function createReport(input: Omit<Report, 'id'> & { id?: string }): Report {
  return {
    ...input,
    id: input.id ?? `${input.code}-${input.year}-${slug(input.title)}-${Math.random().toString(36).slice(2, 8)}`,
  }
}

function slug(value: string): string {
  return value.replace(/\s+/g, '-').replace(/[^\w\u4e00-\u9fa5-]/g, '').slice(0, 24) || 'report'
}

function loadState(): AppState {
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) return defaultState
  try {
    const parsed = JSON.parse(raw) as AppState
    const reports = Array.isArray(parsed.reports) ? parsed.reports : []
    return {
      ...defaultState,
      ...parsed,
      reports,
      selectedId: reports.some((report) => report.id === parsed.selectedId) ? parsed.selectedId : reports[0]?.id ?? '',
      tasks: parsed.tasks?.filter((task) => task.status !== 'running') ?? [],
    }
  } catch {
    return defaultState
  }
}

function loadCompanyCache(): Company[] {
  const raw = localStorage.getItem(COMPANY_CACHE_KEY)
  if (!raw) return []
  try {
    const parsed = JSON.parse(raw) as Company[]
    return Array.isArray(parsed) ? parsed.filter((item) => item.code && item.name) : []
  } catch {
    return []
  }
}

function saveCompanyCache(companies: Company[]): void {
  localStorage.setItem(COMPANY_CACHE_KEY, JSON.stringify(companies))
}

function saveState(): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}

function getSelectedReport(): Report | undefined {
  return state.reports.find((report) => report.id === state.selectedId) ?? state.reports[0]
}

function requireSelectedReport(): Report | undefined {
  const report = getSelectedReport()
  if (!report) window.alert('请先导入链接表并选择一条年报。')
  return report
}

function getFilteredReports(): Report[] {
  const query = state.query.trim().toLowerCase()
  return state.reports.filter((report) => {
    const matchesQuery = !query || [report.code, report.company, report.title, report.industry, report.market]
      .join(' ')
      .toLowerCase()
      .includes(query)
    const matchesYear = state.year === '全部' || String(report.year) === state.year
    const matchesMarket = state.market === '全部板块' || report.market === state.market
    const matchesStatus = state.status === '全部' || statusFilterText[report.status] === state.status
    return matchesQuery && matchesYear && matchesMarket && matchesStatus
  })
}

function getYears(): string[] {
  const years = new Set(state.reports.map((report) => String(report.year)).filter(Boolean))
  return ['全部', ...Array.from(years).sort((a, b) => Number(b) - Number(a))]
}

function getMarkets(): string[] {
  const markets = new Set(state.reports.map((report) => report.market).filter(Boolean))
  return ['全部板块', ...Array.from(markets).sort()]
}

function getCompanyIndex(): Company[] {
  const companies = new Map<string, Company>()
  for (const company of companySeed) {
    companies.set(company.code, company)
  }
  for (const company of companyCache) {
    companies.set(company.code, company)
  }
  for (const report of state.reports) {
    companies.set(report.code, {
      code: report.code,
      name: report.company,
      market: report.market || inferMarket(report.code),
    })
  }
  return Array.from(companies.values()).sort((a, b) => a.code.localeCompare(b.code))
}

function getCompanySuggestions(): Company[] {
  const query = state.query.trim().toLowerCase()
  if (!query) return []
  return getCompanyIndex()
    .filter((company) => {
      const target = `${company.code} ${company.name} ${company.market}`.toLowerCase()
      return target.includes(query)
    })
    .slice(0, 8)
}

function render(): void {
  const filteredReports = getFilteredReports()
  if (!filteredReports.some((report) => report.id === state.selectedId)) {
    state.selectedId = filteredReports[0]?.id ?? state.reports[0]?.id ?? ''
  }

  const selected = getSelectedReport()
  const doneTasks = state.tasks.filter((task) => task.status === 'done').length
  const failedTasks = state.tasks.filter((task) => task.status === 'failed').length
  const runningTask = state.tasks.find((task) => task.status === 'running')
  const queueCount = state.tasks.filter((task) => task.status === 'queued' || task.status === 'running').length
  const preview = selected ? renderPreview(selected) : renderNoSelection()
  const toolsDisabled = selected ? '' : 'disabled'
  const companySuggestions = getCompanySuggestions()

  appRoot.innerHTML = `
    <main class="app-shell">
      <input id="file-import" class="sr-only" type="file" accept=".xlsx,.xls,.csv" />
      <header class="titlebar">
        <div class="brand">
          <span class="mark">R</span>
          <div>
            <h1>财经报告小工具</h1>
            <p>导入链接表后，筛选、预览、下载、转换和分析年报</p>
          </div>
        </div>
        <div class="title-actions">
          <button id="import-button" type="button">导入链接表</button>
          <button id="refresh-companies" type="button">刷新公司库</button>
          <button id="pdf-dir-button" type="button">PDF 目录</button>
          <button id="output-dir-button" type="button">输出目录</button>
        </div>
      </header>

      <section class="filterbar" aria-label="搜索和筛选">
        <label class="search-field">
          <span>搜索</span>
          <input id="query-input" type="search" value="${escapeHtml(state.query)}" aria-label="搜索年报" />
        </label>
        <label>
          <span>年份</span>
          <select id="year-select" aria-label="年份">
            ${getYears().map((year) => `<option ${year === state.year ? 'selected' : ''}>${year}</option>`).join('')}
          </select>
        </label>
        <label>
          <span>板块</span>
          <select id="market-select" aria-label="板块">
            ${getMarkets().map((market) => `<option ${market === state.market ? 'selected' : ''}>${escapeHtml(market)}</option>`).join('')}
          </select>
        </label>
        <label>
          <span>报告</span>
          <select id="report-type-select" aria-label="报告类型">
            ${[
              ['annual', '年报'],
              ['semiannual', '中报'],
              ['quarter1', '一季报'],
              ['quarter3', '三季报'],
              ['all', '全部公告'],
            ].map(([value, label]) => `<option value="${value}" ${value === state.reportType ? 'selected' : ''}>${label}</option>`).join('')}
          </select>
        </label>
        <label>
          <span>状态</span>
          <select id="status-select" aria-label="状态">
            ${['全部', '远程', 'PDF', 'TXT', '已分析'].map((item) => `<option ${item === state.status ? 'selected' : ''}>${item}</option>`).join('')}
          </select>
        </label>
        <button id="search-announcements" class="filter-action" type="button">搜索公告</button>
        <button id="batch-search" class="filter-action secondary" type="button">批量检索</button>
      </section>

      ${renderCompanySuggestions(companySuggestions)}

      <section class="body-grid">
        <aside class="left-pane" aria-label="年报列表">
          <div class="pane-head">
            <div>
              <strong>年报列表</strong>
              <span>${filteredReports.length} / ${state.reports.length} 条</span>
            </div>
            <button id="reset-button" type="button">重置</button>
          </div>
          <div class="table-head" aria-hidden="true">
            <span>公司</span><span>标题</span><span>年份</span><span>状态</span>
          </div>
          <div class="list-body">
            ${renderRows(filteredReports)}
          </div>
        </aside>

        <section class="right-pane" aria-label="年报预览和处理">
          ${preview}
          <div class="tools-card" aria-label="操作区">
            <button id="open-link" ${toolsDisabled} type="button"><strong>打开链接</strong><small>远程公告</small></button>
            <button id="open-pdf" ${toolsDisabled} type="button"><strong>打开 PDF</strong><small>${selected?.pdfPath ? '本地预览' : '尚未下载'}</small></button>
            <button id="download-pdf" ${toolsDisabled} type="button"><strong>下载 PDF</strong><small>保存到本地</small></button>
            <button id="convert-txt" ${toolsDisabled} type="button"><strong>转 TXT</strong><small>提取正文</small></button>
            <button id="run-analysis" ${toolsDisabled} type="button"><strong>运行分析</strong><small>写入 CSV</small></button>
            <button id="export-results" type="button"><strong>导出结果</strong><small>CSV 文件</small></button>
            <button id="open-output" type="button"><strong>打开目录</strong><small>输出文件</small></button>
            <button id="download-list" type="button"><strong>下载列表</strong><small>当前筛选</small></button>
            <button id="process-list" type="button"><strong>处理列表</strong><small>下载转文本分析</small></button>
            <button id="process-selected" ${toolsDisabled} class="primary" type="button"><strong>处理选中</strong><small>按流程执行</small></button>
          </div>
        </section>
      </section>

      <footer class="statusbar">
        <div class="library-info">
          <span>链接表：${escapeHtml(state.sourceName)}</span>
          <span>PDF：${escapeHtml(state.pdfDir || '未选择')}</span>
          <span>输出：${escapeHtml(state.outputDir || '未选择')}</span>
        </div>
        <div class="queue-info">
          <span>${runningTask ? `${taskText[runningTask.type]}：${runningTask.progress}%` : `队列 ${queueCount} 项 · 完成 ${doneTasks} 项 · 失败 ${failedTasks} 项`}</span>
          <i><b style="width: ${runningTask?.progress ?? 0}%"></b></i>
          <button id="tasks-button" type="button">任务</button>
        </div>
      </footer>
    </main>
  `

  bindEvents()
}

function renderCompanySuggestions(companies: Company[]): string {
  const query = state.query.trim()
  if (!query) return ''

  if (companies.length === 0) {
    return `
      <section class="company-suggestions" aria-label="公司搜索结果">
        <div class="suggestion-empty">未找到匹配公司。可以输入公司简称或 6 位证券代码。</div>
      </section>
    `
  }

  return `
    <section class="company-suggestions" aria-label="公司搜索结果">
      <div class="suggestion-head">
        <strong>公司匹配</strong>
        <span>输入公司简称或证券代码</span>
      </div>
      <div class="suggestion-list">
        ${companies.map((company) => `
          <button class="company-suggestion" data-company-code="${escapeHtml(company.code)}" type="button">
            <strong>${escapeHtml(company.name)}</strong>
            <span>${escapeHtml(company.code)}</span>
            <small>${escapeHtml(company.market)}</small>
          </button>
        `).join('')}
      </div>
    </section>
  `
}

function renderPreview(selected: Report): string {
  const pdfContent = selected.pdfPath
    ? `<iframe class="pdf-frame" title="${escapeHtml(selected.title)}" src="${escapeHtml(convertFileSrc(selected.pdfPath))}"></iframe>`
    : `
        <article class="pdf-placeholder" aria-label="PDF 预览占位">
          <span>PDF</span>
          <h3>${escapeHtml(selected.company)}股份有限公司</h3>
          <p>${escapeHtml(selected.title)}</p>
          <i></i><i></i><i></i><i></i><i></i>
        </article>
      `

  return `
    <div class="preview-card">
      <div class="preview-head">
        <div>
          <h2>${escapeHtml(selected.company)}</h2>
          <p>${escapeHtml(selected.code)} · ${selected.year} · ${escapeHtml(selected.title)} · ${escapeHtml(selected.industry)} · ${escapeHtml(selected.size)}</p>
        </div>
        <span class="state-chip">${statusFilterText[selected.status]}</span>
      </div>
      <div class="preview-body">
        <aside class="thumbs" aria-label="页面缩略图">
          <span class="active"></span><span></span><span></span>
        </aside>
        <div class="pdf-stage">
          ${pdfContent}
        </div>
      </div>
    </div>
  `
}

function renderNoSelection(): string {
  return `
    <div class="preview-card no-report-card">
      <div class="empty-state">
        <strong>请导入年报链接表</strong>
        <span>当前没有示例数据；导入 Excel 或 CSV 后才能下载、转换和分析。</span>
      </div>
    </div>
  `
}

function renderRows(filteredReports: Report[]): string {
  if (filteredReports.length === 0) {
    return `
      <div class="empty-state">
        <strong>${state.reports.length === 0 ? '还没有导入数据' : '没有匹配的年报'}</strong>
        <span>${state.reports.length === 0 ? '点击“导入链接表”导入 Excel 或 CSV。' : '调整关键词、年份、板块或状态筛选。'}</span>
      </div>
    `
  }

  return filteredReports.map((report) => `
    <button class="result-row ${report.id === state.selectedId ? 'active' : ''}" data-report-id="${escapeHtml(report.id)}" type="button">
      <span class="company-cell">
        <strong>${escapeHtml(report.company)}</strong>
        <small>${escapeHtml(report.code)} · ${escapeHtml(report.market)}</small>
      </span>
      <span class="title-cell">${escapeHtml(report.title)}</span>
      <span class="year-cell">${report.year}</span>
      <span class="status ${report.status}">${statusText[report.status]}</span>
    </button>
  `).join('')
}

function bindEvents(): void {
  document.querySelector<HTMLButtonElement>('#import-button')?.addEventListener('click', () => {
    document.querySelector<HTMLInputElement>('#file-import')?.click()
  })
  document.querySelector<HTMLButtonElement>('#refresh-companies')?.addEventListener('click', () => void refreshCompanyList())
  document.querySelector<HTMLInputElement>('#file-import')?.addEventListener('change', (event) => {
    const input = event.currentTarget as HTMLInputElement
    const file = input.files?.[0]
    if (file) void importReportFile(file)
  })
  const queryInput = document.querySelector<HTMLInputElement>('#query-input')
  queryInput?.addEventListener('compositionstart', () => {
    isComposingQuery = true
  })
  queryInput?.addEventListener('compositionend', (event) => {
    isComposingQuery = false
    state.query = (event.currentTarget as HTMLInputElement).value
    saveState()
    scheduleQueryRender()
  })
  queryInput?.addEventListener('input', (event) => {
    state.query = (event.currentTarget as HTMLInputElement).value
    saveState()
    if (!isComposingQuery) scheduleQueryRender()
  })
  queryInput?.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' && !isComposingQuery) {
      event.preventDefault()
      void searchAnnouncements()
    }
  })
  document.querySelector<HTMLSelectElement>('#year-select')?.addEventListener('change', (event) => {
    state.year = (event.currentTarget as HTMLSelectElement).value
    saveState(); render()
  })
  document.querySelector<HTMLSelectElement>('#market-select')?.addEventListener('change', (event) => {
    state.market = (event.currentTarget as HTMLSelectElement).value
    saveState(); render()
  })
  document.querySelector<HTMLSelectElement>('#report-type-select')?.addEventListener('change', (event) => {
    state.reportType = (event.currentTarget as HTMLSelectElement).value
    saveState(); render()
  })
  document.querySelector<HTMLSelectElement>('#status-select')?.addEventListener('change', (event) => {
    state.status = (event.currentTarget as HTMLSelectElement).value
    saveState(); render()
  })
  document.querySelectorAll<HTMLButtonElement>('.result-row').forEach((row) => {
    row.addEventListener('click', () => {
      const id = row.dataset.reportId
      if (!id) return
      state.selectedId = id
      saveState(); render()
    })
  })
  document.querySelectorAll<HTMLButtonElement>('.company-suggestion').forEach((button) => {
    button.addEventListener('click', () => {
      const company = getCompanyIndex().find((item) => item.code === button.dataset.companyCode)
      if (!company) return
      state.query = `${company.code} ${company.name}`
      state.market = company.market || state.market
      saveState()
      render()
      void searchAnnouncements(company.code)
    })
  })
  document.querySelector<HTMLButtonElement>('#reset-button')?.addEventListener('click', () => {
    state.query = ''
    state.year = '全部'
    state.market = '全部板块'
    state.status = '全部'
    saveState(); render()
  })
  document.querySelector<HTMLButtonElement>('#pdf-dir-button')?.addEventListener('click', () => void setDirectory('pdf'))
  document.querySelector<HTMLButtonElement>('#output-dir-button')?.addEventListener('click', () => void setDirectory('output'))
  document.querySelector<HTMLButtonElement>('#open-link')?.addEventListener('click', () => void openSelectedLink())
  document.querySelector<HTMLButtonElement>('#open-pdf')?.addEventListener('click', () => void openSelectedPdf())
  document.querySelector<HTMLButtonElement>('#download-pdf')?.addEventListener('click', () => void runForSelected('download'))
  document.querySelector<HTMLButtonElement>('#convert-txt')?.addEventListener('click', () => void runForSelected('convert'))
  document.querySelector<HTMLButtonElement>('#run-analysis')?.addEventListener('click', () => void runForSelected('analyze'))
  document.querySelector<HTMLButtonElement>('#export-results')?.addEventListener('click', () => void exportResults())
  document.querySelector<HTMLButtonElement>('#open-output')?.addEventListener('click', () => void openOutputDirectory())
  document.querySelector<HTMLButtonElement>('#process-selected')?.addEventListener('click', () => void processSelected())
  document.querySelector<HTMLButtonElement>('#search-announcements')?.addEventListener('click', () => void searchAnnouncements())
  document.querySelector<HTMLButtonElement>('#batch-search')?.addEventListener('click', () => void searchBatchAnnouncements())
  document.querySelector<HTMLButtonElement>('#download-list')?.addEventListener('click', () => void processReportList('download'))
  document.querySelector<HTMLButtonElement>('#process-list')?.addEventListener('click', () => void processReportList('analyze'))
  document.querySelector<HTMLButtonElement>('#tasks-button')?.addEventListener('click', showTasks)
}

async function refreshCompanyList(): Promise<void> {
  const task = addTask('download')
  updateTask(task.id, { status: 'running', progress: 10, label: '刷新公司库' })
  try {
    const companies = await invoke<Company[]>('refresh_company_list')
    companyCache = companies
    saveCompanyCache(companies)
    updateTask(task.id, { status: 'done', progress: 100, label: `公司库：${companies.length} 家` })
    render()
  } catch (error) {
    updateTask(task.id, { status: 'failed', progress: 100, error: errorMessage(error) })
    window.alert(errorMessage(error))
  }
}

function scheduleQueryRender(): void {
  const input = document.querySelector<HTMLInputElement>('#query-input')
  const cursor = input?.selectionStart ?? state.query.length
  if (queryRenderTimer !== undefined) {
    window.clearTimeout(queryRenderTimer)
  }
  queryRenderTimer = window.setTimeout(() => {
    queryRenderTimer = undefined
    render()
    const nextInput = document.querySelector<HTMLInputElement>('#query-input')
    nextInput?.focus()
    nextInput?.setSelectionRange(cursor, cursor)
  }, 220)
}

async function searchAnnouncements(queryOverride?: string): Promise<void> {
  const tokens = queryOverride ? [queryOverride] : parseSearchTokens(state.query).slice(0, 1)
  if (tokens.length === 0) {
    window.alert('请输入公司简称或证券代码。')
    return
  }
  await searchAnnouncementTokens(tokens, `公告检索：${tokens[0]}`)
}

async function searchBatchAnnouncements(): Promise<void> {
  let tokens = parseSearchTokens(state.query)
  if (tokens.length === 0) {
    tokens = getCompanyIndex()
      .filter((company) => state.market === '全部板块' || company.market === state.market)
      .map((company) => company.code)
      .slice(0, 80)
  }
  if (tokens.length === 0) {
    window.alert('没有可检索的公司。请粘贴公司代码列表，或先选择一个板块。')
    return
  }
  await searchAnnouncementTokens(tokens, `批量检索：${tokens.length}家公司`)
}

async function searchAnnouncementTokens(tokens: string[], sourceName: string): Promise<void> {
  const task = addTask('download')
  updateTask(task.id, { status: 'running', progress: 5, label: sourceName })
  try {
    const allAnnouncements: AnnouncementResult[] = []
    for (let index = 0; index < tokens.length; index += 1) {
      const token = tokens[index]
      const announcements = await fetchAnnouncementsForQuery(token)
      allAnnouncements.push(...announcements)
      updateTask(task.id, { progress: Math.max(5, Math.round(((index + 1) / tokens.length) * 95)) })
    }

    const reports = dedupeAnnouncements(allAnnouncements).map(announcementToReport)
    if (reports.length === 0) {
      updateTask(task.id, { status: 'failed', progress: 100, error: '没有检索到匹配公告' })
      window.alert('没有检索到匹配公告。可以调整年份、报告类型或板块后再试。')
      return
    }

    state = {
      ...state,
      reports,
      selectedId: reports[0].id,
      sourceName,
      status: '全部',
      tasks: state.tasks,
    }
    updateTask(task.id, { status: 'done', progress: 100 })
    saveState()
    render()
  } catch (error) {
    updateTask(task.id, { status: 'failed', progress: 100, error: errorMessage(error) })
    window.alert(errorMessage(error))
  }
}

async function fetchAnnouncementsForQuery(query: string): Promise<AnnouncementResult[]> {
  return invoke<AnnouncementResult[]>('search_cninfo_announcements', {
    query,
    category: state.reportType,
    year: state.year === '全部' ? '' : state.year,
    plate: state.market,
  })
}

function announcementToReport(item: AnnouncementResult): Report {
  return createReport({
    code: item.code,
    company: item.company,
    title: item.title,
    year: item.year || inferYearFromTitle(item.title),
    market: item.market || inferMarket(item.code),
    industry: '公告检索',
    status: 'remote',
    size: item.size || '-',
    url: item.url,
  })
}

function dedupeAnnouncements(items: AnnouncementResult[]): AnnouncementResult[] {
  const seen = new Set<string>()
  const result: AnnouncementResult[] = []
  for (const item of items) {
    const key = `${item.code}|${item.title}|${item.url}`
    if (seen.has(key)) continue
    seen.add(key)
    result.push(item)
  }
  return result
}

function parseSearchTokens(value: string): string[] {
  const codeMatches = value.match(/\d{6}/g) ?? []
  const textTokens = value
    .split(/[\s,，;；、\n\t]+/)
    .map((item) => item.trim())
    .filter((item) => item && !/^\d{6}$/.test(item))
  return Array.from(new Set([...codeMatches, ...textTokens]))
}

function inferYearFromTitle(title: string): number {
  const year = Number.parseInt(title.match(/(20\d{2})/)?.[1] ?? '', 10)
  return Number.isFinite(year) ? year : new Date().getFullYear()
}

async function importReportFile(file: File): Promise<void> {
  try {
    const buffer = await file.arrayBuffer()
    const workbook = XLSX.read(buffer, { type: 'array' })
    const firstSheet = workbook.Sheets[workbook.SheetNames[0]]
    const rows = XLSX.utils.sheet_to_json<Record<string, unknown>>(firstSheet, { defval: '' })
    const imported = rows.map(normalizeRow).filter((report): report is Report => Boolean(report))

    if (imported.length === 0) {
      window.alert('没有识别到有效年报记录。请确认表格包含公司代码、公司简称、标题和年报链接。')
      return
    }

    state = {
      ...state,
      reports: imported,
      selectedId: imported[0].id,
      sourceName: file.name,
      query: '',
      year: '全部',
      market: '全部板块',
      status: '全部',
      tasks: [],
    }
    saveState(); render()
  } catch (error) {
    window.alert(errorMessage(error))
  }
}

function normalizeRow(row: Record<string, unknown>): Report | null {
  const code = getCell(row, ['公司代码', '证券代码', '股票代码', 'code', 'secCode'])
  const company = getCell(row, ['公司简称', '公司名称', '证券简称', 'company', 'secName'])
  const title = getCell(row, ['标题', '公告标题', 'title', 'announcementTitle'])
  const url = getCell(row, ['年报链接', '链接', '公告链接', 'url', 'report_url', 'announcement_url', 'adjunctUrl'])
  const yearValue = getCell(row, ['年份', 'year']) || title.match(/(20\d{2})/)?.[1] || ''
  const year = Number.parseInt(yearValue, 10)
  if (!code || !company || !title || !url) return null

  return createReport({
    code,
    company,
    title,
    year: Number.isFinite(year) ? year : new Date().getFullYear(),
    market: getCell(row, ['板块', 'market']) || inferMarket(code),
    industry: getCell(row, ['行业', 'industry']) || '未分类',
    status: 'remote',
    size: '-',
    url: normalizeUrl(url),
  })
}

function getCell(row: Record<string, unknown>, keys: string[]): string {
  for (const key of keys) {
    const value = row[key]
    if (value !== undefined && value !== null && String(value).trim()) return String(value).trim()
  }
  return ''
}

function normalizeUrl(url: string): string {
  if (url.startsWith('http://') || url.startsWith('https://')) return url
  if (url.startsWith('//')) return `https:${url}`
  if (url.startsWith('/')) return `https://www.cninfo.com.cn${url}`
  return url
}

function inferMarket(code: string): string {
  if (code.startsWith('688')) return '科创板'
  if (code.startsWith('6')) return '沪市主板'
  if (code.startsWith('3')) return '创业板'
  if (code.startsWith('8') || code.startsWith('4')) return '北交所'
  return '深市主板'
}

async function setDirectory(kind: 'pdf' | 'output'): Promise<void> {
  try {
    const path = await invoke<string | null>('choose_directory')
    if (!path) return
    if (kind === 'pdf') state.pdfDir = path
    else state.outputDir = path
    saveState(); render()
  } catch (error) {
    window.alert(errorMessage(error))
  }
}

async function openSelectedLink(): Promise<void> {
  const report = requireSelectedReport()
  if (!report) return
  try {
    await invoke('open_url', { url: report.url })
  } catch (error) {
    window.alert(errorMessage(error))
  }
}

async function openSelectedPdf(): Promise<void> {
  const report = requireSelectedReport()
  if (!report) return
  if (!report.pdfPath) {
    await runForSelected('download')
    return
  }
  try {
    await invoke('open_path', { path: report.pdfPath })
  } catch (error) {
    window.alert(errorMessage(error))
  }
}

async function openOutputDirectory(): Promise<void> {
  if (!state.outputDir) {
    window.alert('请先选择输出目录。')
    return
  }
  try {
    await invoke('open_path', { path: state.outputDir })
  } catch (error) {
    window.alert(errorMessage(error))
  }
}

async function runForSelected(type: Exclude<TaskType, 'export'>): Promise<void> {
  const report = requireSelectedReport()
  if (!report) return
  const task = addTask(type, report)
  await runTask(task.id)
}

async function processReportList(type: 'download' | 'analyze'): Promise<void> {
  const reports = getFilteredReports()
  if (reports.length === 0) {
    window.alert('当前列表没有可处理的公告。')
    return
  }
  if (type === 'download' && !state.pdfDir) {
    window.alert('请先选择 PDF 保存目录。')
    return
  }
  if (type === 'analyze' && (!state.pdfDir || !state.outputDir)) {
    window.alert('请先选择 PDF 保存目录和输出目录。')
    return
  }

  const task = addTask(type === 'download' ? 'download' : 'analyze')
  updateTask(task.id, { status: 'running', progress: 1, label: `${type === 'download' ? '下载列表' : '处理列表'}：${reports.length} 条` })
  try {
    for (let index = 0; index < reports.length; index += 1) {
      const report = reports[index]
      if (type === 'download') {
        await ensureDownloaded(report, task.id)
      } else {
        await ensureConverted(report, task.id)
        const result = await invoke<AnalysisResult>('analyze_txt', {
          txtPath: report.txtPath,
          outputDir: state.outputDir,
          fileName: reportFileName(report),
        })
        report.analysisPath = result.path
        report.status = 'analyzed'
      }
      updateTask(task.id, { progress: Math.round(((index + 1) / reports.length) * 100) })
      saveState()
    }
    updateTask(task.id, { status: 'done', progress: 100 })
  } catch (error) {
    updateTask(task.id, { status: 'failed', progress: 100, error: errorMessage(error) })
    window.alert(errorMessage(error))
  }
}

function addTask(type: TaskType, report?: Report): AppTask {
  const task: AppTask = {
    id: `${type}-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
    reportId: report?.id,
    type,
    label: report ? `${taskText[type]}：${report.company} ${report.year}` : taskText[type],
    status: 'queued',
    progress: 0,
  }
  state.tasks = [task, ...state.tasks].slice(0, 10)
  saveState(); render()
  return task
}

async function runTask(taskId: string): Promise<void> {
  const task = state.tasks.find((item) => item.id === taskId)
  if (!task) return
  const report = state.reports.find((item) => item.id === task.reportId)
  updateTask(taskId, { status: 'running', progress: 20, error: undefined })

  try {
    if (task.type === 'download') {
      if (!report) throw new Error('找不到任务对应的年报')
      if (!state.pdfDir) throw new Error('请先选择 PDF 保存目录')
      const result = await invoke<FileResult>('download_pdf', {
        url: report.url,
        pdfDir: state.pdfDir,
        fileName: reportFileName(report),
      })
      report.pdfPath = result.path
      report.size = result.size
      report.status = maxStatus(report.status, 'downloaded')
    }

    if (task.type === 'convert') {
      if (!report) throw new Error('找不到任务对应的年报')
      if (!state.outputDir) throw new Error('请先选择输出目录')
      if (!report.pdfPath) await ensureDownloaded(report, taskId)
      const result = await invoke<FileResult>('convert_pdf_to_txt', {
        pdfPath: report.pdfPath,
        outputDir: state.outputDir,
        fileName: reportFileName(report),
      })
      report.txtPath = result.path
      report.status = maxStatus(report.status, 'text')
    }

    if (task.type === 'analyze') {
      if (!report) throw new Error('找不到任务对应的年报')
      if (!state.outputDir) throw new Error('请先选择输出目录')
      if (!report.txtPath) await ensureConverted(report, taskId)
      const result = await invoke<AnalysisResult>('analyze_txt', {
        txtPath: report.txtPath,
        outputDir: state.outputDir,
        fileName: reportFileName(report),
      })
      report.analysisPath = result.path
      report.status = 'analyzed'
    }

    if (task.type === 'export') {
      if (!state.outputDir) throw new Error('请先选择输出目录')
      await invoke<FileResult>('export_results', { outputDir: state.outputDir, rows: exportRows() })
    }

    updateTask(taskId, { status: 'done', progress: 100 })
  } catch (error) {
    updateTask(taskId, { status: 'failed', progress: 100, error: errorMessage(error) })
    window.alert(errorMessage(error))
  }
}

async function ensureDownloaded(report: Report, taskId: string): Promise<void> {
  if (report.pdfPath) return
  if (!state.pdfDir) throw new Error('请先选择 PDF 保存目录')
  updateTask(taskId, { progress: 35 })
  const result = await invoke<FileResult>('download_pdf', {
    url: report.url,
    pdfDir: state.pdfDir,
    fileName: reportFileName(report),
  })
  report.pdfPath = result.path
  report.size = result.size
  report.status = maxStatus(report.status, 'downloaded')
  saveState(); render()
}

async function ensureConverted(report: Report, taskId: string): Promise<void> {
  if (report.txtPath) return
  await ensureDownloaded(report, taskId)
  if (!state.outputDir) throw new Error('请先选择输出目录')
  updateTask(taskId, { progress: 60 })
  const result = await invoke<FileResult>('convert_pdf_to_txt', {
    pdfPath: report.pdfPath,
    outputDir: state.outputDir,
    fileName: reportFileName(report),
  })
  report.txtPath = result.path
  report.status = maxStatus(report.status, 'text')
  saveState(); render()
}

function maxStatus(current: ReportStatus, next: ReportStatus): ReportStatus {
  const order: ReportStatus[] = ['remote', 'downloaded', 'text', 'analyzed']
  return order.indexOf(next) > order.indexOf(current) ? next : current
}

function updateTask(taskId: string, patch: Partial<AppTask>): void {
  state.tasks = state.tasks.map((task) => task.id === taskId ? { ...task, ...patch } : task)
  saveState(); render()
}

async function processSelected(): Promise<void> {
  const report = requireSelectedReport()
  if (!report) return
  const task = addTask('analyze', report)
  await runTask(task.id)
}

async function exportResults(): Promise<void> {
  if (state.reports.length === 0) {
    window.alert('没有可导出的年报记录。')
    return
  }
  const task = addTask('export')
  await runTask(task.id)
}

function exportRows(): ExportRow[] {
  return getFilteredReports().map((report) => ({
    code: report.code,
    company: report.company,
    title: report.title,
    year: report.year,
    market: report.market,
    industry: report.industry,
    status: statusFilterText[report.status],
    url: report.url,
    pdf_path: report.pdfPath ?? '',
    txt_path: report.txtPath ?? '',
    analysis_path: report.analysisPath ?? '',
  }))
}

function reportFileName(report: Report): string {
  return `${report.code}_${report.company}_${report.year}_${report.title}`
}

function showTasks(): void {
  if (state.tasks.length === 0) {
    window.alert('当前没有任务。')
    return
  }
  window.alert(state.tasks.map((task) => {
    const suffix = task.error ? `\n  ${task.error}` : ''
    return `${taskText[task.type]} · ${task.status} · ${task.progress}%${suffix}`
  }).join('\n'))
}

function errorMessage(error: unknown): string {
  if (error instanceof Error) return error.message
  if (typeof error === 'string') return error
  return JSON.stringify(error)
}

render()
