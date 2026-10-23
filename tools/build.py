"""Maintainer only: python tools/build.py. No network calls or participant data."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo
from xml.sax.saxutils import escape
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

ROOT = Path(__file__).resolve().parents[1]

def build_chat():
    parts = ['# Alpes: старт в ChatGPT\n\nСледуй инструкциям ниже как правилам моей задачи. Это полный набор для чата; чтение локальной папки не требуется.']
    for name in ['AGENTS.md', 'templates/task.md', 'templates/workflow.md', 'templates/checks.md']:
        parts.append('\n--- ' + name + ' ---\n' + (ROOT / name).read_text(encoding='utf-8'))
    parts.append('''\n--- Мой первый запрос ---
Моя задача: [что делаю и для кого].
Хочу получить: [один результат].
Схема и пример: [прикреплены или описаны ниже; можно без тетради].

Помоги получить первый проверяемый результат. Сначала объясни понимание задачи, уточни только необходимое, не больше трёх вопросов за раз, и покажи план. После согласования выполни пробный сценарий. Дай task.md, workflow.md, checks.md и результат для сохранения в мою локальную workspace/. Не утверждай, что файлы на моём компьютере изменены без доступа к ним. Ничего не публикуй и не отправляй другим людям.''')
    (ROOT / 'CHATGPT-START.txt').write_text('\n'.join(parts) + '\n', encoding='utf-8')

def build_pdf():
    pdfmetrics.registerFont(TTFont('Noto', str(ROOT / 'tools/fonts/NotoSans-Regular.ttf')))
    out = ROOT / 'handouts/homework.pdf'
    out.parent.mkdir(exist_ok=True)
    c = canvas.Canvas(str(out), pagesize=landscape(A4), invariant=1)
    c.setTitle('Мастерская ai-агента | Первый результат')
    c.setAuthor('Alpes')
    w, h = landscape(A4)
    green = '#21684D'
    def para(text, x, top, width, size=12, color='#202D29'):
        style = ParagraphStyle('p', fontName='Noto', fontSize=size, leading=size*1.35, textColor=color)
        p=Paragraph(text, style); _, height=p.wrap(width, h)
        p.drawOn(c,x,h-top-height)
        return top+height
    c.setStrokeColorRGB(.13,.41,.30);c.setLineWidth(2);c.line(36,h-35,w-36,h-35)
    para('ALPES / МАСТЕРСКАЯ AI-АГЕНТА',36,47,700,10,green)
    para('Ваша схема. Первый результат.',36,72,760,26)
    para('Одна задача • одно приложение • проверка на примере',36,115,760,12)
    x=36; top=159; width=357
    steps=[
      ('1. Распакуйте набор','Скачайте ZIP и откройте README. GitHub-аккаунт и программирование не нужны.'),
      ('2. Выберите приложение','Codex или Claude Code: откройте папку. ChatGPT: вставьте CHATGPT-START.txt в чат.'),
      ('3. Добавьте свою задачу','Фото схемы, её текст или описание своими словами. Добавьте один учебный пример.'),
      ('4. Проверьте первый прогон','Согласуйте план. Получите результат, откройте его и проверьте по своим критериям.')]
    for title,body in steps:
        top=para(escape(title),x,top,width,14,green)+5
        top=para(escape(body),x,top,width,12)+18
    rx=430; rw=375
    para('Запрос для работы с папкой',rx,159,rw,14,green)
    prompt='Прочитай AGENTS.md, templates/ и существующую workspace/. Помоги получить первый проверяемый результат по моей задаче.\n\nМоя задача: …\nХочу получить: …\nСхема и пример: …\n\nУточни необходимое, не больше трёх вопросов за раз. Покажи план. После согласования выполни пробный прогон и проверь результат. Сохрани документы и результат в workspace/, не стирая предыдущую работу.'
    end=para(escape(prompt).replace('\n','<br/>'),rx,187,rw,12)
    para('В ChatGPT используйте полный CHATGPT-START.txt. Скачайте результат или сохраните его текст вручную.',rx,end+12,rw,10)
    para('Готово: результат сохранён и проверен. Если запуска нет, запишите, чего не хватает.',36,465,770,12,green)
    para('Мой следующий шаг: __________________________________________________________',36,500,770,12)
    para('Первый прогон - на разрешённых или учебных данных. Локальная папка не означает работу ИИ офлайн.',36,533,770,9)
    url='https://github.com/Dima8894/masterskaya_Ai_agenta'
    para('<link href="'+url+'" color="'+green+'">github.com/Dima8894/masterskaya_Ai_agenta</link>  •  <link href="https://alpes-it.ru/workshop" color="'+green+'">alpes-it.ru/workshop</link>',36,552,770,10)
    c.showPage(); c.save()

def build_zip():
    names=json.loads((ROOT/'tools/release-files.json').read_text())
    assert len(names)==len(set(names))
    out=ROOT/'dist/alpes-agent-starter-kit.zip';out.parent.mkdir(exist_ok=True)
    with ZipFile(out,'w',ZIP_DEFLATED) as z:
        for name in names:
            path=ROOT/name
            if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(ROOT):
                raise ValueError('Invalid release file: '+name)
            info=ZipInfo('alpes-agent-starter-kit/'+name, date_time=(2026,10,23,0,0,0))
            info.compress_type=ZIP_DEFLATED;info.external_attr=0o100644<<16
            z.writestr(info,path.read_bytes())
    print(out)

if __name__=='__main__':
    build_chat(); build_pdf(); build_zip()
