use serde::{Deserialize, Serialize};
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

#[derive(Debug, Serialize)]
struct FileResult {
    path: String,
    size: String,
}

#[derive(Debug, Serialize)]
struct AnalysisResult {
    path: String,
    total_chars: usize,
    keyword_hits: usize,
}

#[derive(Debug, Serialize)]
struct AnnouncementResult {
    code: String,
    company: String,
    title: String,
    year: i32,
    market: String,
    url: String,
    size: String,
}

#[derive(Debug, Serialize)]
struct CompanyResult {
    code: String,
    name: String,
    market: String,
}

#[derive(Debug, Deserialize)]
struct ExportRow {
    code: String,
    company: String,
    title: String,
    year: i32,
    market: String,
    industry: String,
    status: String,
    url: String,
    pdf_path: String,
    txt_path: String,
    analysis_path: String,
}

#[tauri::command]
fn choose_directory() -> Result<Option<String>, String> {
    let output = Command::new("osascript")
        .args([
            "-e",
            "POSIX path of (choose folder with prompt \"选择目录\")",
        ])
        .output()
        .map_err(|err| format!("打开目录选择器失败: {err}"))?;

    if output.status.success() {
        let path = String::from_utf8_lossy(&output.stdout).trim().to_string();
        if path.is_empty() {
            Ok(None)
        } else {
            Ok(Some(trim_trailing_slash(&path)))
        }
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        if stderr.contains("User canceled") || stderr.contains("-128") {
            Ok(None)
        } else {
            Err(format!("选择目录失败: {}", stderr.trim()))
        }
    }
}

#[tauri::command]
fn open_url(url: String) -> Result<(), String> {
    if !(url.starts_with("http://") || url.starts_with("https://")) {
        return Err("只允许打开 http/https 链接".to_string());
    }
    run_open(&url)
}

#[tauri::command]
fn open_path(path: String) -> Result<(), String> {
    let expanded = expand_home(&path);
    if !expanded.exists() {
        return Err(format!("路径不存在: {}", expanded.display()));
    }
    run_open(&expanded.to_string_lossy())
}

#[tauri::command]
fn download_pdf(url: String, pdf_dir: String, file_name: String) -> Result<FileResult, String> {
    if !(url.starts_with("http://") || url.starts_with("https://")) {
        return Err("年报链接不是有效的 http/https 地址".to_string());
    }

    let dir = ensure_dir(&pdf_dir)?;
    let target = dir.join(format!("{}.pdf", sanitize_file_stem(&file_name)));
    let part = dir.join(format!("{}.pdf.part", sanitize_file_stem(&file_name)));

    if target.exists() && is_pdf(&target)? {
        return Ok(FileResult {
            path: target.to_string_lossy().to_string(),
            size: human_size(fs::metadata(&target).map_err(|err| err.to_string())?.len()),
        });
    }

    let status = Command::new("curl")
        .args([
            "--fail",
            "--location",
            "--retry",
            "2",
            "--connect-timeout",
            "20",
            "--max-time",
            "180",
            "--user-agent",
            "Mozilla/5.0 FinancialReportTool/0.1",
            "--output",
        ])
        .arg(&part)
        .arg(&url)
        .status()
        .map_err(|err| format!("启动 curl 下载失败: {err}"))?;

    if !status.success() {
        let _ = fs::remove_file(&part);
        return Err(format!("PDF 下载失败，curl 退出码: {:?}", status.code()));
    }

    if !is_pdf(&part)? {
        let _ = fs::remove_file(&part);
        return Err("下载结果不是有效 PDF 文件".to_string());
    }

    fs::rename(&part, &target).map_err(|err| format!("保存 PDF 失败: {err}"))?;
    let size = fs::metadata(&target).map_err(|err| err.to_string())?.len();

    Ok(FileResult {
        path: target.to_string_lossy().to_string(),
        size: human_size(size),
    })
}

#[tauri::command]
fn convert_pdf_to_txt(
    pdf_path: String,
    output_dir: String,
    file_name: String,
) -> Result<FileResult, String> {
    let pdf = expand_home(&pdf_path);
    if !pdf.exists() {
        return Err(format!("PDF 不存在: {}", pdf.display()));
    }
    if !is_pdf(&pdf)? {
        return Err(format!("不是有效 PDF: {}", pdf.display()));
    }

    let dir = ensure_dir(&output_dir)?;
    let txt = dir.join(format!("{}.txt", sanitize_file_stem(&file_name)));

    if command_exists("pdftotext") {
        let status = Command::new("pdftotext")
            .args(["-layout", "-enc", "UTF-8"])
            .arg(&pdf)
            .arg(&txt)
            .status()
            .map_err(|err| format!("启动 pdftotext 失败: {err}"))?;
        if status.success() && txt.exists() {
            return Ok(file_result(txt));
        }
    }

    let script = r#"
import sys
pdf_path, txt_path = sys.argv[1], sys.argv[2]
errors = []
try:
    from pypdf import PdfReader
    reader = PdfReader(pdf_path)
    with open(txt_path, 'w', encoding='utf-8') as f:
        for page in reader.pages:
            f.write(page.extract_text() or '')
            f.write('\n')
    sys.exit(0)
except Exception as exc:
    errors.append('pypdf: ' + str(exc))
try:
    from PyPDF2 import PdfReader
    reader = PdfReader(pdf_path)
    with open(txt_path, 'w', encoding='utf-8') as f:
        for page in reader.pages:
            f.write(page.extract_text() or '')
            f.write('\n')
    sys.exit(0)
except Exception as exc:
    errors.append('PyPDF2: ' + str(exc))
try:
    from pdfminer.high_level import extract_text
    text = extract_text(pdf_path)
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(text)
    sys.exit(0)
except Exception as exc:
    errors.append('pdfminer: ' + str(exc))
sys.stderr.write('\n'.join(errors))
sys.exit(1)
"#;

    let output = Command::new("python3")
        .arg("-c")
        .arg(script)
        .arg(&pdf)
        .arg(&txt)
        .output()
        .map_err(|err| format!("启动 python3 转换失败: {err}"))?;

    if output.status.success() && txt.exists() {
        Ok(file_result(txt))
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        Err(format!(
            "PDF 转 TXT 失败。请安装 pdftotext、pypdf、PyPDF2 或 pdfminer.six。{}",
            stderr.trim()
        ))
    }
}

#[tauri::command]
fn analyze_txt(
    txt_path: String,
    output_dir: String,
    file_name: String,
) -> Result<AnalysisResult, String> {
    let txt = expand_home(&txt_path);
    if !txt.exists() {
        return Err(format!("TXT 不存在: {}", txt.display()));
    }

    let text = fs::read_to_string(&txt).map_err(|err| format!("读取 TXT 失败: {err}"))?;
    let keywords = [
        "营业收入",
        "净利润",
        "现金流",
        "资产负债",
        "研发",
        "风险",
        "分红",
        "毛利率",
        "应收账款",
        "存货",
    ];
    let dir = ensure_dir(&output_dir)?;
    let csv = dir.join(format!("{}_analysis.csv", sanitize_file_stem(&file_name)));
    let mut rows = String::from("keyword,count\n");
    let mut keyword_hits = 0usize;
    for keyword in keywords {
        let count = text.matches(keyword).count();
        keyword_hits += count;
        rows.push_str(&format!("{},{}\n", csv_escape(keyword), count));
    }
    rows.push_str(&format!(
        "{},{}\n",
        csv_escape("总字符数"),
        text.chars().count()
    ));
    fs::write(&csv, rows).map_err(|err| format!("写入分析结果失败: {err}"))?;

    Ok(AnalysisResult {
        path: csv.to_string_lossy().to_string(),
        total_chars: text.chars().count(),
        keyword_hits,
    })
}

#[tauri::command]
fn export_results(output_dir: String, rows: Vec<ExportRow>) -> Result<FileResult, String> {
    let dir = ensure_dir(&output_dir)?;
    let path = dir.join("financial-report-results.csv");
    let mut csv = String::from(
        "公司代码,公司简称,标题,年份,板块,行业,状态,年报链接,PDF路径,TXT路径,分析路径\n",
    );

    for row in rows {
        csv.push_str(
            &[
                row.code,
                row.company,
                row.title,
                row.year.to_string(),
                row.market,
                row.industry,
                row.status,
                row.url,
                row.pdf_path,
                row.txt_path,
                row.analysis_path,
            ]
            .into_iter()
            .map(|value| csv_escape(&value))
            .collect::<Vec<_>>()
            .join(","),
        );
        csv.push('\n');
    }

    fs::write(&path, csv).map_err(|err| format!("导出 CSV 失败: {err}"))?;
    Ok(file_result(path))
}

#[tauri::command]
fn refresh_company_list() -> Result<Vec<CompanyResult>, String> {
    let output = Command::new("curl")
        .args([
            "--silent",
            "--show-error",
            "--fail",
            "--location",
            "--connect-timeout",
            "15",
            "--max-time",
            "30",
            "-H",
            "User-Agent: Mozilla/5.0 FinancialReportTool/0.1",
            "-H",
            "Referer: https://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search",
            "https://www.cninfo.com.cn/new/data/szse_stock.json",
        ])
        .output()
        .map_err(|err| format!("刷新公司库失败: {err}"))?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(format!("刷新公司库失败: {}", stderr.trim()));
    }

    let data: serde_json::Value =
        serde_json::from_slice(&output.stdout).map_err(|err| format!("解析公司库失败: {err}"))?;
    let stock_list = data
        .get("stockList")
        .and_then(|value| value.as_array())
        .ok_or_else(|| "公司库响应缺少 stockList 字段".to_string())?;

    let mut companies = Vec::new();
    for item in stock_list {
        if json_string(item, "category") != "A股" {
            continue;
        }
        let code = json_string(item, "code");
        let name = json_string(item, "zwjc");
        if code.is_empty() || name.is_empty() {
            continue;
        }
        companies.push(CompanyResult {
            market: infer_market_from_code(&code),
            code,
            name,
        });
    }
    Ok(companies)
}

#[tauri::command]
fn search_cninfo_announcements(
    query: String,
    category: String,
    year: String,
    plate: String,
) -> Result<Vec<AnnouncementResult>, String> {
    let query = query.trim();
    if query.is_empty() {
        return Err("请输入公司简称或证券代码".to_string());
    }

    let category = match category.as_str() {
        "annual" => "category_ndbg_szsh",
        "semiannual" => "category_bndbg_szsh",
        "quarter1" => "category_yjdbg_szsh",
        "quarter3" => "category_sjdbg_szsh",
        "all" => "",
        other => other,
    };
    let plate = match plate.as_str() {
        "all" | "全部板块" => "sz;sh;bj",
        "sz" | "深市" | "深市主板" | "创业板" => "sz",
        "sh" | "沪市" | "沪市主板" | "科创板" => "sh",
        "bj" | "北交所" => "bj",
        other => other,
    };
    let se_date = if let Ok(report_year) = year.parse::<i32>() {
        format!("{}-01-01~{}-12-31", report_year, report_year + 2)
    } else {
        "2020-01-01~2027-12-31".to_string()
    };

    let output = Command::new("curl")
        .args([
            "--silent",
            "--show-error",
            "--fail",
            "--location",
            "--connect-timeout",
            "15",
            "--max-time",
            "30",
            "-H",
            "Accept: */*",
            "-H",
            "Content-Type: application/x-www-form-urlencoded; charset=UTF-8",
            "-H",
            "Origin: https://www.cninfo.com.cn",
            "-H",
            "Referer: https://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search",
            "-H",
            "User-Agent: Mozilla/5.0 FinancialReportTool/0.1",
            "-H",
            "X-Requested-With: XMLHttpRequest",
            "--data-urlencode",
            "pageNum=1",
            "--data-urlencode",
            "pageSize=50",
            "--data-urlencode",
            "column=szse",
            "--data-urlencode",
            "tabName=fulltext",
            "--data-urlencode",
        ])
        .arg(format!("plate={plate}"))
        .arg("--data-urlencode")
        .arg(format!("searchkey={query}"))
        .args(["--data-urlencode", "secid="])
        .arg("--data-urlencode")
        .arg(format!("category={category}"))
        .args(["--data-urlencode", "trade="])
        .arg("--data-urlencode")
        .arg(format!("seDate={se_date}"))
        .args(["--data-urlencode", "sortName=time"])
        .args(["--data-urlencode", "sortType=desc"])
        .args(["--data-urlencode", "isHLtitle=false"])
        .arg("https://www.cninfo.com.cn/new/hisAnnouncement/query")
        .output()
        .map_err(|err| format!("启动巨潮公告检索失败: {err}"))?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(format!("巨潮公告检索失败: {}", stderr.trim()));
    }

    let data: serde_json::Value = serde_json::from_slice(&output.stdout)
        .map_err(|err| format!("解析巨潮公告响应失败: {err}"))?;
    let announcements = data
        .get("announcements")
        .and_then(|value| value.as_array())
        .ok_or_else(|| "巨潮公告响应缺少公告列表".to_string())?;

    let mut results = Vec::new();
    for item in announcements {
        let title = json_string(item, "announcementTitle");
        if title.is_empty() {
            continue;
        }
        if let Ok(report_year) = year.parse::<i32>() {
            if !title.contains(&report_year.to_string()) {
                continue;
            }
        }
        let adjunct_url = json_string(item, "adjunctUrl");
        if adjunct_url.is_empty() {
            continue;
        }
        let code = json_string(item, "secCode");
        results.push(AnnouncementResult {
            market: infer_market_from_code(&code),
            year: infer_year_from_title(&title).unwrap_or(0),
            code,
            company: json_string(item, "secName"),
            title,
            url: format!("https://static.cninfo.com.cn/{adjunct_url}"),
            size: item
                .get("adjunctSize")
                .and_then(|value| value.as_i64())
                .map(|kb| human_size((kb.max(0) as u64) * 1024))
                .unwrap_or_else(|| "-".to_string()),
        });
    }

    Ok(results)
}

fn run_open(target: &str) -> Result<(), String> {
    let status = Command::new("open")
        .arg(target)
        .status()
        .map_err(|err| format!("启动系统打开失败: {err}"))?;
    if status.success() {
        Ok(())
    } else {
        Err(format!("系统打开失败，退出码: {:?}", status.code()))
    }
}

fn ensure_dir(path: &str) -> Result<PathBuf, String> {
    if path.trim().is_empty() {
        return Err("请先选择目录".to_string());
    }
    let dir = expand_home(path);
    fs::create_dir_all(&dir).map_err(|err| format!("创建目录失败 {}: {err}", dir.display()))?;
    Ok(dir)
}

fn expand_home(path: &str) -> PathBuf {
    if path == "~" || path.starts_with("~/") {
        if let Ok(home) = std::env::var("HOME") {
            return PathBuf::from(home).join(path.trim_start_matches("~/"));
        }
    }
    PathBuf::from(path)
}

fn trim_trailing_slash(path: &str) -> String {
    if path == "/" {
        path.to_string()
    } else {
        path.trim_end_matches('/').to_string()
    }
}

fn sanitize_file_stem(value: &str) -> String {
    let mut cleaned = String::new();
    for ch in value.chars() {
        if ch.is_ascii_alphanumeric()
            || ch == '-'
            || ch == '_'
            || ch == '.'
            || ('\u{4e00}'..='\u{9fff}').contains(&ch)
        {
            cleaned.push(ch);
        } else if ch.is_whitespace() {
            cleaned.push('_');
        }
    }
    let cleaned = cleaned.trim_matches('_').to_string();
    if cleaned.is_empty() {
        "report".to_string()
    } else {
        cleaned.chars().take(120).collect()
    }
}

fn is_pdf(path: &Path) -> Result<bool, String> {
    let mut file =
        fs::File::open(path).map_err(|err| format!("打开文件失败 {}: {err}", path.display()))?;
    let mut header = [0u8; 5];
    let n = std::io::Read::read(&mut file, &mut header)
        .map_err(|err| format!("读取文件失败: {err}"))?;
    Ok(n == 5 && &header == b"%PDF-")
}

fn command_exists(command: &str) -> bool {
    Command::new("/usr/bin/env")
        .arg("which")
        .arg(command)
        .output()
        .map(|output| output.status.success())
        .unwrap_or(false)
}

fn file_result(path: PathBuf) -> FileResult {
    let size = fs::metadata(&path)
        .map(|meta| human_size(meta.len()))
        .unwrap_or_else(|_| "-".to_string());
    FileResult {
        path: path.to_string_lossy().to_string(),
        size,
    }
}

fn human_size(bytes: u64) -> String {
    let mb = bytes as f64 / 1024.0 / 1024.0;
    if mb >= 1.0 {
        format!("{mb:.1} MB")
    } else {
        format!("{:.1} KB", bytes as f64 / 1024.0)
    }
}

fn csv_escape(value: &str) -> String {
    if value.contains(',') || value.contains('"') || value.contains('\n') || value.contains('\r') {
        format!("\"{}\"", value.replace('"', "\"\""))
    } else {
        value.to_string()
    }
}

fn json_string(value: &serde_json::Value, key: &str) -> String {
    value
        .get(key)
        .and_then(|item| item.as_str())
        .unwrap_or_default()
        .to_string()
}

fn infer_market_from_code(code: &str) -> String {
    if code.starts_with("688") {
        "科创板".to_string()
    } else if code.starts_with('6') {
        "沪市主板".to_string()
    } else if code.starts_with('3') {
        "创业板".to_string()
    } else if code.starts_with('8') || code.starts_with('4') {
        "北交所".to_string()
    } else {
        "深市主板".to_string()
    }
}

fn infer_year_from_title(title: &str) -> Option<i32> {
    for year in 1990..=2035 {
        if title.contains(&year.to_string()) {
            return Some(year);
        }
    }
    None
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            choose_directory,
            open_url,
            open_path,
            download_pdf,
            convert_pdf_to_txt,
            analyze_txt,
            export_results,
            search_cninfo_announcements,
            refresh_company_list
        ])
        .setup(|app| {
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
