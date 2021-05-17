import os
from typing import List

from scraping import Article


def generate_html(path: str, name: str, articles: List[Article]):
    rows = [
        f"""
    <tr data-annotation="{a.annotation}"
        data-page_url="{a.page_url}"
        data-document_url="{a.document_url}">
        <td>{i}</td>
        <td>{a.name}</td>
        <td>{a.author}</td>
        <td><a href="{a.source_url}">{a.source_url}</a></td>
    </tr>
    """
        for i, a in enumerate(articles, start=1)
    ]

    html = f"""
<!doctype html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>{name} ({len(articles)} шт.)</title>
    
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.24/css/jquery.dataTables.min.css">
    <style> 
    body {{
        font-family: Arial;
        display: none;
    }}
    
    table {{width:100%}}
    
    tr {{cursor: pointer}}
    
    #selected-wrapper {{
        display: flex;
        justify-content: center;
        align-items: center;
        
        position: absolute;
        z-index: 1;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        
        cursor: pointer;
        background-color: rgba(200,200,200,0.55);
    }}
    
    #selected {{
        display: flex;
        flex-flow: column;
        justify-content: space-between;
        height: fit-content;
        min-width: 400px;
        min-height: 400px;
        max-width: 800px;
        margin: 20px;
        padding: 20px;
        
        cursor: default;
        background-color: white;
        border-radius: 7px;
        box-shadow: 0 0 5px #8080803b;
    }}
    
    #urls {{
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    
    </style>

    <script src="https://code.jquery.com/jquery-3.5.1.js"></script>
    <script src="https://cdn.datatables.net/1.10.24/js/jquery.dataTables.min.js"></script>
    <script>
      $("body").css('opacity', 0);
      $(document).ready(function() {{
        const table = $("table")
        const wrapper = $("#selected-wrapper")
        const name = $("#name")
        const author = $("#author")
        const annotation = $("#annotation")
        const page_url = $("#page-url")
        const document_url = $("#document-url")
        
        table.DataTable({{
            "pageLength": 15
        }})
        table.on("click", "tr", function () {{
           const tr = $(this)
           name.text($(tr.children()[1]).text())
           author.text($(tr.children()[2]).text())
           annotation.text(tr.data("annotation"))            
           page_url.text(tr.data("page_url"))
           page_url.attr("href", tr.data("page_url"))
           document_url.text(tr.data("document_url"))
           document_url.attr("href", tr.data("document_url"))
           wrapper.css("display", "flex")
        }})
        
        wrapper.css("display", "none")
        wrapper.click(e => {{
            if ($(e.target).is("#selected-wrapper")) 
                wrapper.css("display", "none")                
        }})
        document.body.style.display = 'block'
      }})
    </script>
</head>
<body>

<div id="selected-wrapper">
    <div id="selected">
        <div>
            <h2 id="name">name</h1>
            <h4 id="author">author</h4>
            <p id="annotation">annotation</p>
        </div>
        <div id="urls">
            <h5>Источник статьи:</h5>
            <a id="page-url" target="_blank" rel="noopener noreferrer"></a>
            <h5>Ссылка на скачивание статьи:</h5>
            <a id="document-url" target="_blank" rel="noopener noreferrer"></a>
        </div>
    </div>
</div>

<table class="display">
    <thead>
    <tr>
        <th>№</th>
        <th>Тема</th>
        <th>Автор</th>
        <th>Источник</th>
    </tr>
    </thead>
    
    <tbody>
    {''.join(rows)}
    </tbody>
    
    <tfoot>
    </tfoot>
</table>

</body>
</html>
"""
    with open(path, "w") as file:
        file.write(html)


def open_html(path: str):
    os.system(f"browse {path}")
