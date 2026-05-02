from flask import Flask, request, redirect, url_for, flash, send_file, render_template_string
import os
import requests
from datetime import datetime

BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET')

def validate_submission(form):
    errors = []

    tg = form.get('telegram', '').strip()
    if not tg:
        errors.append('Telegram Username/ID is required.')

    uid = form.get('uid', '').strip()
    if not uid:
        errors.append('Free Fire UID is required.')
    else:
        if not uid.isdigit():
            errors.append('Free Fire UID must be a number.')
        else:
            val = int(uid)
            if val < 10000001 or val > 1500000000000:
                errors.append('Free Fire UID must be between 10000001 and 1500000000000.')

    map_codes = form.getlist("map_codes[]")

    if not map_codes:
        errors.append("At least one map code is required.")
    else:
        for code in map_codes:
            if not code.startswith("#"):
                errors.append(f"Invalid map code: {code}")

    if len(map_codes) > 6:
      errors.append("Maximum 6 maps allowed.")

    tc1 = form.get('tc1')
    tc2 = form.get('tc2')
    tc3 = form.get('tc3')
    if not (tc1 and tc2 and tc3):
        errors.append('You must check all three Terms & Conditions boxes.')

    return errors

FORM_HTML = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Free Fire Craftmate - Submission</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {
      background: #f5f5f7;
    }
    .card {
      border-radius: 1rem;
    }
    .form-section {
      padding: 1rem;
      border-radius: 0.75rem;
      background: #ffffff;
      box-shadow: 0 0.25rem 0.5rem rgba(0,0,0,0.1);
      margin-bottom: 1rem;
    }
    .btn-primary {
      background: linear-gradient(90deg,#ff5858,#f857a6);
      border: none;
    }
    .btn-primary:hover {
      opacity: 0.9;
    }
    .form-check-label {
      cursor: pointer;
    }
    .input-group-text {
      background-color: #f0f0f0;
    }
  </style>
</head>
<body>
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-lg-8 col-md-10 col-sm-12">
        <div class="card shadow-sm p-4">
          <h1 class="mb-3 text-center">Free Fire Craftmate</h1>
          <p class="text-center text-muted mb-4">Submit your entries for Craftmate below</p>

          {% with messages = get_flashed_messages() %}
            {% if messages %}
              <div class="alert alert-danger">
                <ul class="mb-0">
                {% for m in messages %}
                  <li>{{ m }}</li>
                {% endfor %}
                </ul>
              </div>
            {% endif %}
          {% endwith %}

          <form method="post" action="{{ url_for('submit') }}">

            <!-- Telegram & UID -->
            <div class="form-section">
              <h5>Account Details</h5>
              <div class="mb-3">
                <label class="form-label">Telegram Username/ID</label>
                <input class="form-control" name="telegram" placeholder="Enter your Telegram username or ID" value="{{ formdata.telegram if formdata else '' }}" required>
                <div class="form-text">If no username, enter numeric Telegram ID</div>
              </div>

              <div class="mb-3">
                <label class="form-label">Free Fire UID</label>
                <input class="form-control" id="uid_value" name="uid" type="number" min="10000001" max="1500000000000" placeholder="12345678" value="{{ formdata.uid if formdata else '' }}" required>
                <div class="form-text">Enter the UID of your primary account. It can be different from the account you are participating with.</div>
                <div id="uid_info" class="mt-2 small text-muted"></div>
              </div>
            </div>

            <!-- Round 1 -->
            <div class="form-section">
            <h5>Map Submission</h5>

            <div class="mb-3">
              <label class="form-label">How many maps do you want to submit?</label>

              <div class="form-check">
                <input class="form-check-input" type="radio" name="submission_type" id="singleMap" value="single" checked>
                <label class="form-check-label" for="singleMap">
                  I want to submit only one map.
                </label>
              </div>

              <div class="form-check">
                <input class="form-check-input" type="radio" name="submission_type" id="multipleMaps" value="multiple">
                <label class="form-check-label" for="multipleMaps">
                  I want to submit more than one map.
                </label>
              </div>
            </div>

            <div id="mapInputs">

              <div class="mb-3 map-input">
                <label class="form-label">Map Code</label>
                <input class="form-control map-code" name="map_codes[]" placeholder="#FREEFIRE..." required>
                <div class="map-info mt-2 small text-muted"></div>
              </div>

            </div>

            <div id="mapCounterControls" class="d-none">
              <button type="button" class="btn btn-outline-secondary btn-sm" id="addMapBtn">
                + Add another map
              </button>
              <span class="text-muted ms-2">(Max 6 maps)</span>
            </div>

          </div>

            <!-- Terms -->
            <div class="form-section">
              <h5>Terms & Conditions</h5>
              <div class="form-check mb-2">
                <input class="form-check-input" type="checkbox" id="tc1" name="tc1">
                <label class="form-check-label" for="tc1">I have read and understood the <a href=/rules target="_blank">rules</a> of this contest.</label>
              </div>
              <div class="form-check mb-2">
                <input class="form-check-input" type="checkbox" id="tc2" name="tc2">
                <label class="form-check-label" for="tc2">I solemnly affirm that my entry follows the <a href="https://content.garena.com/legal/toc/toc_en.html" target="_blank">UGC Policies</a> of Garena.</label>
              </div>
              <div class="form-check mb-2">
                <input class="form-check-input" type="checkbox" id="tc3" name="tc3">
                <label class="form-check-label" for="tc3">The information submitted through this form is true and accurate.</label>
              </div>
            </div>

            <button class="btn btn-primary w-100 py-2 mt-3" type="submit">Submit</button>
          </form>
        </div>
      </div>
    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
<script>

function debounce(fn, delay) {
  let timer = null;
  return function(...args) {
    clearTimeout(timer);
    timer = setTimeout(() => {
      fn.apply(this, args);
    }, delay);
  };
}

async function fetchAccountInfoDebounced(inputId, infoId, region="ind") {
  const uid = document.getElementById(inputId).value.trim();
  const infoBox = document.getElementById(infoId);
  if (!uid) {
    infoBox.innerHTML = "";
    return;
  }

  try {
    infoBox.innerHTML = "Loading...";
    const res = await fetch(`/account_info?uid=${encodeURIComponent(uid)}&region=${region}`);
    const data = await res.json();
    if (data.basicInfo) {
      const m = data.basicInfo;
      infoBox.innerHTML = `
        <div class="alert alert-info p-2 mt-2">
          <b>${m.nickname}</b><br>
          Lv.${m.level}
        </div>
      `;
    } else {
      infoBox.innerHTML = "<span class='text-danger'>Not found</span>";
    }
  } catch (err) {
    infoBox.innerHTML = "<span class='text-danger'>Error fetching info</span>";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const uidInput = document.getElementById("uid_value");
  const uidInfo = "uid_info";
  if (uidInput) {
    const debouncedFetch = debounce(() => fetchAccountInfoDebounced("uid_value", uidInfo), 1000);
    uidInput.addEventListener("input", debouncedFetch);
    uidInput.addEventListener("blur", () => fetchAccountInfoDebounced("uid_value", uidInfo)); // fetch on blur too
  }
});

document.addEventListener("DOMContentLoaded", () => {

  const singleRadio = document.getElementById("singleMap");
  const multiRadio = document.getElementById("multipleMaps");
  const mapContainer = document.getElementById("mapInputs");
  const addBtn = document.getElementById("addMapBtn");
  const counterControls = document.getElementById("mapCounterControls");

  let mapCount = 1;
  const maxMaps = 6;

  function toggleMapMode() {

    if (singleRadio.checked) {

      counterControls.classList.add("d-none");

      while (mapContainer.children.length > 1) {
        mapContainer.removeChild(mapContainer.lastChild);
      }

      mapCount = 1;
    }

    if (multiRadio.checked) {
      counterControls.classList.remove("d-none");
    }

  }

  singleRadio.addEventListener("change", toggleMapMode);
  multiRadio.addEventListener("change", toggleMapMode);

  addBtn.addEventListener("click", () => {

    if (mapCount >= maxMaps) return;

    mapCount++;

    const div = document.createElement("div");
    div.className = "mb-3 map-input";

    div.innerHTML = `
      <label class="form-label">Map Code ${mapCount}</label>
      <input class="form-control map-code" name="map_codes[]" placeholder="#FREEFIRE..." required>
      <div class="map-info mt-2 small text-muted"></div>
    `;

    mapContainer.appendChild(div);

  });

});

document.addEventListener("input", function(e) {

  if (!e.target.classList.contains("map-code")) return;

  const code = e.target.value.trim();
  const infoBox = e.target.parentElement.querySelector(".map-info");

  if (!code.startsWith("#")) {
    infoBox.innerHTML = "<span class='text-danger'>Code must start with #</span>";
    return;
  }

  fetch(`/map_info?code=${encodeURIComponent(code)}`)
  .then(res => res.json())
  .then(data => {

    if (data.map_info) {

      const m = data.map_info;

      infoBox.innerHTML = `
        <div class="alert alert-info p-2 mt-2">
          <b>${m.map_name}</b><br>
          Creator: ${m.nickname}<br>
          Likes: ${m.liked}
        </div>
      `;

    }

  });

});

</script>
</html>
'''

@app.route('/')
def index():
    return render_template_string(FORM_HTML)

@app.route('/rules')
def rules():
    return send_file("rules.pdf", mimetype='application/pdf')

@app.route('/account_info')
def account_info():
    uid = request.args.get('uid', '').strip()
    if not uid:
        return {"error": "Missing UID"}, 400

    regions = ['ind', 'sg', 'br']
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/140.0.0.0 Safari/537.36"
        )
    }

    for region in regions:
        url = f"https://ff.ggbluewhale.store/api/data?region={region}&uid={uid}&key=Craftmate"
        app.logger.info(f"Fetching account info from region: {region} ({url})")

        try:
            r = requests.get(url, headers=headers, timeout=10)
            app.logger.info(f"Region {region} -> Status: {r.status_code}, Body: {r.text[:200]}")

            if r.status_code == 200:
                try:
                    data = r.json()
                    return data, 200
                except Exception:
                    return {
                        "error": "Failed to parse JSON",
                        "region": region,
                        "status_code": r.status_code,
                        "text": r.text
                    }, 500

        except Exception as e:
            app.logger.error(f"Error fetching from region {region}: {e}")

    return {"error": "Invalid UID"}, 400


@app.route('/map_info')
def map_info():
    code = request.args.get('code', '').strip()
    if not code.startswith('#'):
        return {"error": "Invalid map code"}, 400
    
    if code.startswith("#"):
        code = code.replace("#", "")

    regions = ['ind', 'sg', 'br']

    for region in regions:
        url = f"https://map-info.craftland.ff.ggbluewhale.store/api/{region}?code={code}&key=Craftmate"
        app.logger.info(f"Fetching map info from region: {region} ({url})")

        try:
            r = requests.get(url, timeout=10)
            app.logger.info(f"Region {region} -> Status: {r.status_code}, Body: {r.text[:200]}")

            if r.status_code == 200:
                return r.json(), 200

        except Exception as e:
            app.logger.error(f"Error while fetching from {region}: {e}")

    return {"error": "Invalid map code"}, 400


@app.route('/submit', methods=['POST'])
def submit():
    form = request.form

    errors = validate_submission(form)
    if errors:
        for e in errors:
            flash(e)
        return render_template_string(FORM_HTML, formdata=form)

    telegram_username = form.get('telegram').strip()
    uid = form.get('uid').strip()
    map_codes = form.getlist("map_codes[]")
    maps_text = "\n".join([f"Map {i+1}: {c}" for i, c in enumerate(map_codes)])

    text = (
    f"<b>New Craftmate Submission</b>\n"
    f"<b>Telegram:</b> {telegram_username}\n"
    f"<b>Free Fire UID:</b> {uid}\n\n"
    f"<b>Submitted Maps:</b>\n{maps_text}\n\n"
    f"<b>Timestamp (UTC):</b> {datetime.utcnow().isoformat()}"
    )

    send_ok = send_telegram_message(BOT_TOKEN, CHAT_ID, text)

    if not send_ok:
        flash('Failed to send message to Telegram. Please contact the admin.')
        return redirect(url_for('index'))

    return render_template_string('''
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Submission Successful</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {
      background: #f5f5f7;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      text-align: center;
    }
    .card {
      padding: 2rem;
      border-radius: 1rem;
      box-shadow: 0 0.25rem 0.5rem rgba(0,0,0,0.1);
      background: #ffffff;
    }
    .btn-home {
      margin-top: 1.5rem;
      background: linear-gradient(90deg,#ff5858,#f857a6);
      border: none;
      color: white;
    }
    .btn-home:hover {
      opacity: 0.9;
    }
  </style>
</head>
<body>
  <div class="card">
    <h3 class="mb-3">✅ Your entry has been submitted successfully!</h3>
    <p class="text-muted">Thank you for participating in Craftmate.</p>
    <a href="/" class="btn btn-home">Submit Another Entry</a>
  </div>
</body>
</html>
''')

TELEGRAM_API = 'https://api.telegram.org/bot{token}/{method}'

def send_telegram_message(token, chat_id, text):
    url = TELEGRAM_API.format(token=token, method='sendMessage')
    try:
        r = requests.post(url, data={
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }, timeout=10)
        return r.status_code == 200 and r.json().get('ok')
    except Exception as e:
        app.logger.exception('Error sending Telegram message: %s', e)
        return False

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
