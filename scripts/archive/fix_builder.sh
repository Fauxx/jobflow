sed -i '/<\/script>/d' templates/applications/builder.html
cat scratch_js.html >> templates/applications/builder.html
echo "    </script>" >> templates/applications/builder.html
echo "</body>" >> templates/applications/builder.html
echo "</html>" >> templates/applications/builder.html
