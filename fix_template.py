import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace description_url with source_url for existing Jinja template
html = html.replace('job.description_url', 'job.source_url')

# Modify the job list section to include an empty state container for JS
list_section = """
                <div class="flex justify-between items-center mb-3">
                    <h2 class="text-xs font-bold text-gray-400 uppercase tracking-wider px-1">
                        {{ current_status }} Listings (<span id="job-count-display">{{ jobs|length }}</span>)
                    </h2>
                </div>
                
                <div id="job-list-container" class="space-y-3">
"""
html = re.sub(r'<div class="flex justify-between items-center mb-3">.*?<h2 class="text-xs font-bold text-gray-400 uppercase tracking-wider px-1">.*?</h2>.*?</div>', list_section, html, flags=re.DOTALL)

# Add pagination controls at the bottom of the section (just before </section>)
pagination_html = """
                </div>
                <div id="pagination-controls" class="hidden flex justify-between items-center mt-4 px-1">
                    <button id="prev-page" class="text-xs bg-gray-700 hover:bg-gray-600 text-white py-1 px-3 rounded transition">Previous</button>
                    <span id="page-info" class="text-xs text-gray-400">Page 1</span>
                    <button id="next-page" class="text-xs bg-gray-700 hover:bg-gray-600 text-white py-1 px-3 rounded transition">Next</button>
                </div>
"""
html = html.replace('</section>', pagination_html + '\n            </section>')

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)
