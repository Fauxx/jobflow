with open("templates/dashboard.html", "r") as f:
    content = f.read()

# The modal starts with "    <!-- JD Edit Modal -->" and ends with "    </div>\n        function runScraper()" (Wait, no, runScraper is JS).
# Let's just find the JD Edit modal block and move it before `<script>`.
# Better yet, let's just find where it starts and ends.
start_idx = content.find("    <!-- JD Edit Modal -->")
# The modal ends with "    </div>" right before "        function runScraper()"
end_idx = content.find("        function runScraper()")

if start_idx != -1 and end_idx != -1:
    modal_html = content[start_idx:end_idx]
    
    # Remove it from the current position
    content = content[:start_idx] + content[end_idx:]
    
    # It might have left <script> before start_idx. Let's make sure.
    # We want to put modal_html BEFORE <script>
    script_idx = content.find("<script>")
    if script_idx != -1:
        content = content[:script_idx] + modal_html + content[script_idx:]
        
with open("templates/dashboard.html", "w") as f:
    f.write(content)
