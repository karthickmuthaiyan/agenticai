from flask import Flask, render_template_string, request
from utils.gutenberg_tool_calling import answer_question
from utils.gutenberg_tool_calling_structured_output import answer_question as answer_question_structured

app = Flask(__name__)


# -------------------------------------------------------------------
# Single-page application shell
# -------------------------------------------------------------------

INDEX_TEMPLATE = """
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>AI Demos</title>

    <style>
        :root {
            font-family: Inter, ui-sans-serif, system-ui, sans-serif;
            color: #e8eefc;
            background: #0b1020;
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            height: 100vh;
            overflow: hidden;
            background:
                radial-gradient(
                    circle at top right,
                    #26366d 0,
                    #0b1020 48%
                );
        }

        /* Main application layout */
        .app {
            display: flex;
            height: 100vh;
        }

        /* ---------------------------------------------------------
           LEFT SIDEBAR
           --------------------------------------------------------- */

        .sidebar {
            width: 280px;
            min-width: 280px;
            height: 100vh;

            padding: 28px 18px;

            background: rgba(11, 16, 32, 0.88);
            border-right: 1px solid rgba(154, 174, 232, 0.16);

            backdrop-filter: blur(16px);

            display: flex;
            flex-direction: column;
        }

        .brand {
            color: #ffffff;
            text-decoration: none;

            font-size: 1.15rem;
            font-weight: 800;
            letter-spacing: .04em;

            padding: 0 10px 30px;
        }

        .sidebar-title {
            color: #7f8db5;
            font-size: .72rem;
            font-weight: 700;
            letter-spacing: .1em;
            text-transform: uppercase;

            padding: 0 10px 10px;
        }

        .demo-list {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .demo-button {
            width: 100%;

            padding: 13px 14px;

            border: 1px solid transparent;
            border-radius: 10px;

            background: transparent;
            color: #aebce0;

            font-size: .95rem;
            text-align: left;

            cursor: pointer;

            transition:
                background .2s ease,
                color .2s ease,
                border-color .2s ease;
        }

        .demo-button:hover {
            background: rgba(124, 92, 255, .12);
            color: #ffffff;
        }

        .demo-button.active {
            background: linear-gradient(
                135deg,
                rgba(124, 92, 255, .25),
                rgba(79, 140, 255, .15)
            );

            border-color: rgba(124, 92, 255, .35);
            color: #ffffff;
        }

        .sidebar-footer {
            margin-top: auto;
            padding: 15px 10px 0;

            border-top: 1px solid rgba(154, 174, 232, .12);
        }

        .sidebar-footer a {
            color: #7f8db5;
            text-decoration: none;
            font-size: .85rem;
        }

        .sidebar-footer a:hover {
            color: #ffffff;
        }


        /* ---------------------------------------------------------
           RIGHT CONTENT
           --------------------------------------------------------- */

        .content {
            flex: 1;
            height: 100vh;
            min-width: 0;

            display: flex;
            flex-direction: column;
        }

        .content-header {
            height: 72px;
            min-height: 72px;

            display: flex;
            align-items: center;

            padding: 0 28px;

            border-bottom: 1px solid rgba(154, 174, 232, .12);
        }

        .content-header h1 {
            margin: 0;

            font-size: 1.1rem;
            font-weight: 700;
        }

        .content-header span {
            margin-left: 12px;

            color: #6f7da4;
            font-size: .9rem;
        }

        .demo-frame {
            flex: 1;
            width: 100%;
            height: calc(100vh - 72px);

            border: 0;
            background: transparent;
        }


        /* ---------------------------------------------------------
           MOBILE
           --------------------------------------------------------- */

        @media (max-width: 700px) {
            .app {
                flex-direction: column;
            }

            .sidebar {
                width: 100%;
                min-width: 0;
                height: auto;

                padding: 15px;

                border-right: 0;
                border-bottom: 1px solid rgba(154, 174, 232, .16);
            }

            .brand {
                padding: 5px 5px 15px;
            }

            .sidebar-title {
                display: none;
            }

            .demo-list {
                flex-direction: row;
                overflow-x: auto;
            }

            .demo-button {
                width: auto;
                white-space: nowrap;
            }

            .sidebar-footer {
                display: none;
            }

            .content {
                height: calc(100vh - 120px);
            }

            .content-header {
                height: 60px;
                min-height: 60px;
                padding: 0 18px;
            }

            .demo-frame {
                height: calc(100vh - 180px);
            }
        }
    </style>
</head>

<body>

<div class="app">

    <!-- =========================================================
         LEFT SIDE
         ========================================================= -->

    <aside class="sidebar">

        <a class="brand" href="#" onclick="loadDemo('/', null); return false;">
            ✦ AI DEMOS
        </a>

        <div class="sidebar-title">
            Demo Topics
        </div>

        <div class="demo-list">

            <button
                class="demo-button active"
                data-url="/demo/welcome"
                data-title="Welcome"
                onclick="loadDemo('/demo/welcome', this)"
            >
                🏠 Welcome
            </button>

            <button
                class="demo-button"
                data-url="/answer_question"
                data-title="Search Gutenberg"
                onclick="loadDemo('/answer_question', this)"
            >
                📚 Search Gutenberg
            </button>

            <button
                class="demo-button"
                data-url="/answer_question_structured"
                data-title="Search Gutenberg (Structured)"
                onclick="loadDemo('/answer_question_structured', this)"
            >
                🧩 Gutenberg — Structured
            </button>

        </div>

        <div class="sidebar-footer">
            <a
                href="#"
                onclick="loadDemo('/demo/about', null); return false;"
            >
                About AI Demos →
            </a>
        </div>

    </aside>


    <!-- =========================================================
         RIGHT SIDE
         ========================================================= -->

    <main class="content">

        <header class="content-header">
            <h1 id="demo-title">Welcome</h1>
            <span>AI Demonstrations</span>
        </header>

        <iframe
            id="demo-frame"
            class="demo-frame"
            src="/demo/welcome"
            title="AI Demo"
        ></iframe>

    </main>

</div>


<script>
    function loadDemo(url, button) {

        const frame = document.getElementById("demo-frame");
        const title = document.getElementById("demo-title");

        // Load the selected Flask page on the right.
        frame.src = url;

        // Update title.
        if (button) {
            title.textContent = button.dataset.title;
        }

        // Update active sidebar item.
        document.querySelectorAll(".demo-button").forEach(function(item) {
            item.classList.remove("active");
        });

        if (button) {
            button.classList.add("active");
        }
    }
</script>

</body>
</html>
"""


# -------------------------------------------------------------------
# Demo page template
# -------------------------------------------------------------------

QUERY_TEMPLATE = """
<!doctype html>
<html>
<head>

    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>{{ page_title }}</title>

    <style>

        :root {
            font-family: Inter, ui-sans-serif, system-ui, sans-serif;
            color: #e8eefc;
            background: transparent;
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100%;
            background: transparent;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 45px 35px 80px;
        }

        .card {
            padding: clamp(25px, 5vw, 50px);

            background: rgba(20, 29, 57, .82);

            border: 1px solid rgba(154, 174, 232, .2);
            border-radius: 24px;

            box-shadow: 0 24px 70px rgba(0,0,0,.25);

            backdrop-filter: blur(12px);
        }

        h1 {
            margin-top: 0;
            margin-bottom: 12px;

            font-size: clamp(2rem, 5vw, 3.2rem);
            line-height: 1.1;
        }

        p {
            color: #b8c3df;
            line-height: 1.7;
        }

        label {
            display: block;

            margin: 28px 0 10px;

            color: #b8c3df;
            font-weight: 600;
        }

        input {
            width: 100%;

            padding: 15px 16px;

            border: 1px solid #44527c;
            border-radius: 12px;

            background: #111a35;
            color: #ffffff;

            font-size: 1rem;
        }

        input:focus {
            outline: none;
            border-color: #7c5cff;
            box-shadow: 0 0 0 3px rgba(124, 92, 255, .15);
        }

        button {
            margin-top: 16px;

            padding: 13px 20px;

            border: 0;
            border-radius: 12px;

            background: linear-gradient(
                135deg,
                #7c5cff,
                #4f8cff
            );

            color: #ffffff;
            font-weight: 700;

            cursor: pointer;
        }

        button:hover {
            opacity: .9;
        }

        h2 {
            margin-top: 36px;
        }

        pre {
            padding: 18px;

            overflow: auto;
            white-space: pre-wrap;

            color: #cbd8ff;

            background: #0d1429;

            border-radius: 12px;
        }

        code {
            color: #cbd8ff;
        }

    </style>

</head>

<body>

<div class="container">

    <section class="card">

        <h1>{{ page_title }}</h1>

        <p>
            Submit a query to <code>{{ page_title }}</code>.
        </p>

        <form method="post">

            <label for="query">
                Input query:
            </label>

            <input
                id="query"
                name="query"
                value="{{ query }}"
                placeholder="Ask something..."
                required
            >

            <button type="submit">
                Submit
            </button>

        </form>

        {% if result is not none %}

            <h2>Result</h2>

            <pre>{{ result }}</pre>

        {% endif %}

    </section>

</div>

</body>
</html>
"""


# -------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------

@app.route("/")
def home():
    return render_template_string(INDEX_TEMPLATE)


@app.route("/demo/welcome")
def welcome():
    return render_template_string("""
        <!doctype html>
        <html>
        <head>
            <style>
                body {
                    margin: 0;
                    font-family: Inter, system-ui, sans-serif;
                    color: #e8eefc;
                    background: transparent;
                }

                .welcome {
                    max-width: 900px;
                    margin: 0 auto;
                    padding: 80px 35px;
                }

                h1 {
                    font-size: clamp(2.5rem, 6vw, 4.5rem);
                    line-height: 1.05;
                    margin: 0 0 20px;
                }

                p {
                    max-width: 650px;
                    color: #b8c3df;
                    line-height: 1.8;
                    font-size: 1.1rem;
                }
            </style>
        </head>

        <body>

            <div class="welcome">
                <h1>Explore intelligent ideas.</h1>

                <p>
                    Select a demo from the menu on the left to explore
                    practical demonstrations of modern AI capabilities.
                </p>
            </div>

        </body>
        </html>
    """)


def render_query_page(page_title, answer_function):

    query_text = request.form.get("query", "")
    result = None

    if request.method == "POST":

        try:
            result = answer_function(query_text)

        except Exception as error:
            result = str(error)

    return render_template_string(
        QUERY_TEMPLATE,
        page_title=page_title,
        query=query_text,
        result=result
    )


@app.route("/answer_question", methods=["GET", "POST"])
def answer_question_page():

    return render_query_page(
        "Search Gutenberg",
        answer_question
    )


@app.route("/answer_question_structured", methods=["GET", "POST"])
def answer_question_structured_page():

    return render_query_page(
        "Search Gutenberg (Structured)",
        answer_question_structured
    )


@app.route("/demo/about")
def about():

    return render_template_string("""
        <!doctype html>
        <html>
        <head>
            <style>
                body {
                    margin: 0;
                    font-family: Inter, system-ui, sans-serif;
                    color: #e8eefc;
                    background: transparent;
                }

                .container {
                    max-width: 900px;
                    margin: 0 auto;
                    padding: 70px 35px;
                }

                .card {
                    padding: 45px;

                    background: rgba(20,29,57,.82);

                    border: 1px solid rgba(154,174,232,.2);
                    border-radius: 24px;
                }

                h1 {
                    margin-top: 0;
                    font-size: 3rem;
                }

                p {
                    color: #b8c3df;
                    line-height: 1.8;
                }
            </style>
        </head>

        <body>

            <div class="container">

                <section class="card">

                    <h1>About AI Demos</h1>

                    <p>
                        A collection of focused demonstrations exploring
                        practical, human-friendly AI capabilities.
                    </p>

                </section>

            </div>

        </body>
        </html>
    """)


# -------------------------------------------------------------------
# Run
# -------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
