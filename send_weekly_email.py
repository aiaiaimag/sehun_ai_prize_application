"""
Weekly Email Sender for Art Prize Application Strategy
매주 월요일 자동으로 application_strategy_2026_kr.md를 이메일로 발송
"""

import smtplib
import os
import re
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# === 설정 ===
SENDER_EMAIL = "chltpdpf@gmail.com"
SENDER_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "").replace(" ", "")
RECIPIENT_EMAIL = "erichoi815@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MD_FILE = os.path.join(SCRIPT_DIR, "application_strategy_2026_kr.md")


def read_strategy_file():
    with open(MD_FILE, "r", encoding="utf-8") as f:
        return f.read()


def md_to_html(md):
    """마크다운을 깔끔한 HTML로 변환"""
    lines = md.split("\n")
    html_lines = []
    in_table = False
    in_code = False

    for line in lines:
        stripped = line.strip()

        # 코드 블록
        if stripped.startswith("```"):
            if in_code:
                html_lines.append("</pre></div>")
                in_code = False
            else:
                html_lines.append(
                    '<div style="background:#1a1a2e;border-radius:8px;padding:16px;margin:16px 0;">'
                    '<pre style="color:#e0e0e0;font-family:\'Courier New\',monospace;font-size:13px;margin:0;line-height:1.8;">'
                )
                in_code = True
            continue

        if in_code:
            html_lines.append(stripped)
            continue

        # 테이블
        if "|" in stripped and not stripped.startswith("#"):
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            if all(set(c) <= set("- ") for c in cells):
                continue
            if not in_table:
                html_lines.append(
                    '<table style="width:100%;border-collapse:collapse;margin:8px 0;font-size:11px;">'
                )
                in_table = True
                html_lines.append("<thead><tr>")
                for cell in cells:
                    html_lines.append(
                        f'<th style="background:#2c3e50;color:#fff;padding:10px 14px;text-align:left;'
                        f'font-weight:600;border:1px solid #34495e;">{apply_inline(cell)}</th>'
                    )
                html_lines.append("</tr></thead><tbody>")
            else:
                html_lines.append("<tr>")
                for cell in cells:
                    bg = "#f8f9fa" if len(html_lines) % 2 == 0 else "#fff"
                    html_lines.append(
                        f'<td style="padding:9px 14px;border:1px solid #e0e0e0;background:{bg};">'
                        f'{apply_inline(cell)}</td>'
                    )
                html_lines.append("</tr>")
            continue
        elif in_table:
            html_lines.append("</tbody></table>")
            in_table = False

        # 구분선
        if stripped == "---":
            html_lines.append(
                '<hr style="border:none;height:1px;background:linear-gradient(to right,#e0e0e0,#3498db,#e0e0e0);margin:28px 0;">'
            )
            continue

        # 빈 줄
        if not stripped:
            html_lines.append("<br>")
            continue

        # 헤딩
        if stripped.startswith("# "):
            html_lines.append(
                f'<h1 style="color:#1a1a2e;font-size:18px;font-weight:700;margin:16px 0 6px;'
                f'padding-bottom:8px;border-bottom:3px solid #3498db;">{apply_inline(stripped[2:])}</h1>'
            )
        elif stripped.startswith("## "):
            html_lines.append(
                f'<h2 style="color:#2c3e50;font-size:15px;font-weight:600;margin:16px 0 6px;'
                f'padding-bottom:6px;border-bottom:2px solid #ecf0f1;">{apply_inline(stripped[3:])}</h2>'
            )
        elif stripped.startswith("### "):
            html_lines.append(
                f'<h3 style="color:#34495e;font-size:14px;font-weight:600;margin:14px 0 6px;'
                f'padding:8px 12px;background:#f0f4f8;border-left:4px solid #3498db;border-radius:0 6px 6px 0;">'
                f'{apply_inline(stripped[4:])}</h3>'
            )
        # 리스트
        elif stripped.startswith("- "):
            content = stripped[2:]
            html_lines.append(
                f'<div style="padding:2px 0 2px 16px;margin:1px 0;line-height:1.5;font-size:12px;">'
                f'<span style="color:#3498db;margin-right:6px;">&#9654;</span>{apply_inline(content)}</div>'
            )
        elif re.match(r"^\d+\.", stripped):
            num, content = stripped.split(".", 1)
            html_lines.append(
                f'<div style="padding:2px 0 2px 16px;margin:1px 0;line-height:1.5;font-size:12px;">'
                f'<span style="display:inline-block;width:18px;height:18px;background:#3498db;color:#fff;'
                f'border-radius:50%;text-align:center;line-height:18px;font-size:10px;font-weight:700;'
                f'margin-right:8px;">{num.strip()}</span>{apply_inline(content.strip())}</div>'
            )
        # 일반 텍스트
        else:
            html_lines.append(
                f'<p style="margin:4px 0;line-height:1.6;color:#333;font-size:12px;">{apply_inline(stripped)}</p>'
            )

    if in_table:
        html_lines.append("</tbody></table>")

    return "\n".join(html_lines)


def apply_inline(text):
    """인라인 마크다운 (볼드, 이탤릭, 이모지 등) 처리"""
    # **bold**
    text = re.sub(
        r"\*\*(.+?)\*\*",
        r'<strong style="color:#2c3e50;">\1</strong>',
        text,
    )
    # *italic*
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    # URL을 클릭 가능한 링크로
    text = re.sub(
        r"(https?://[^\s<]+)",
        r'<a href="\1" style="color:#3498db;text-decoration:none;" target="_blank">\1</a>',
        text,
    )
    # 상태 배지
    text = text.replace(
        "⭐",
        '<span style="background:#e74c3c;color:#fff;padding:2px 8px;border-radius:10px;font-size:11px;">중요</span>',
    )
    return text


def send_email():
    if not SENDER_APP_PASSWORD:
        print("ERROR: GMAIL_APP_PASSWORD 환경변수가 설정되지 않았습니다.")
        sys.exit(1)

    content = read_strategy_file()
    today = datetime.now().strftime("%Y-%m-%d")
    body_html = md_to_html(content)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Art Prize 업데이트 - {today}"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL

    # 텍스트 폴백
    text_part = MIMEText(content, "plain", "utf-8")
    msg.attach(text_part)

    # HTML 버전
    html = f"""<!DOCTYPE html>
<html lang="ko">
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f4f6f9;font-family:'Apple SD Gothic Neo','Malgun Gothic','Segoe UI',sans-serif;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6f9;">
    <tr><td align="center" style="padding:24px 16px;">
      <table role="presentation" width="680" cellpadding="0" cellspacing="0"
             style="background:#fff;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,0.08);overflow:hidden;">
        <!-- 날짜 바 -->
        <tr>
          <td style="background:#1a1a2e;padding:14px 28px;">
            <span style="color:#fff;font-size:14px;font-weight:600;">Art Prize - {today} 기준</span>
          </td>
        </tr>
        <!-- 본문 -->
        <tr>
          <td style="padding:20px 28px 28px;font-size:12px;color:#333;line-height:1.6;">
            {body_html}
          </td>
        </tr>
        <!-- 푸터 -->
        <tr>
          <td style="background:#f8f9fa;padding:20px 36px;border-top:1px solid #e8e8e8;">
            <p style="margin:0;color:#999;font-size:12px;text-align:center;">
              이 이메일은 GitHub Actions에 의해 자동 발송되었습니다.<br>
              AI Art Prize Application System &copy; 2026
            </p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""

    html_part = MIMEText(html, "html", "utf-8")
    msg.attach(html_part)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        print(f"[{today}] 이메일 발송 성공! -> {RECIPIENT_EMAIL}")
    except smtplib.SMTPAuthenticationError as e:
        print(f"ERROR: Gmail 인증 실패. 코드: {e.smtp_code}, 메시지: {e.smtp_error}")
        print(f"사용된 이메일: {SENDER_EMAIL}")
        print(f"비밀번호 길이: {len(SENDER_APP_PASSWORD)}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: 이메일 발송 실패 - {e}")
        sys.exit(1)


if __name__ == "__main__":
    send_email()
