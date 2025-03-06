name: AI Training Email
on:
  schedule:
    - cron: '0 12 1,15 * *'  # Runs on 1st and 15th of each month at noon UTC
jobs:
  run_script:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repo
        uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install beautifulsoup4 requests
      - name: Run script
        run: python script.py
