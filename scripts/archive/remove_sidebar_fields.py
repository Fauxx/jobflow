import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Using regex to remove the Sources block
# It starts around <div class="flex justify-between items-center px-2"> and ends after the JobStreet div, just before the "Use Authenticated Session" part
pattern = re.compile(r'<div class="flex justify-between items-center px-2">.*?<label class="block text-xs text-gray-400 font-bold">Sources</label>.*?</label>\s*<p class="text-\[9px\] text-gray-500 mt-1 pl-5">If unchecked, runs search in clean incognito window\.</p>\s*</div>', re.DOTALL)

# Let's write a safer regex or just find/replace using string bounds
start_idx = content.find('<div class="flex justify-between items-center px-2">')
end_str = '<p class="text-[9px] text-gray-500 mt-1 pl-5">If unchecked, runs search in clean incognito window.</p>\n                        </div>'
end_idx = content.find(end_str)

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + content[end_idx + len(end_str):]
else:
    print("Could not find boundaries")

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
