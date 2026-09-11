sed -i '/<!-- Cover Letter Modal (Dashboard) -->/,$d' templates/dashboard.html
cat scratch_dashboard_cl.html >> templates/dashboard.html
echo "</body>\n</html>" >> templates/dashboard.html
