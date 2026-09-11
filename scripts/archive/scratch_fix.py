with open("templates/dashboard.html", "r") as f:
    lines = f.readlines()
    
# Find the exact location of the `{% endif %}` I added and remove it.
new_lines = []
for line in lines:
    if "{% endif %}" in line and "            </div>" in new_lines[-1] and "                {% endif %}" in new_lines[-2] and "                <p class=\"text-gray-600" in new_lines[-3]:
        continue # skip the wrongly placed one
    new_lines.append(line)

# Now, add {% endif %} after `</div>` which follows `{% endfor %}`
final_lines = []
in_job_grid = False
for i, line in enumerate(new_lines):
    final_lines.append(line)
    if "{% endfor %}" in line:
        if i + 1 < len(new_lines) and "</div>" in new_lines[i+1]:
            pass
for i, line in enumerate(new_lines):
    if "{% endfor %}" in line:
        # the next line should be </div>
        pass

with open("templates/dashboard.html", "w") as f:
    for line in new_lines:
        f.write(line)
