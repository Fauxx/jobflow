import re

with open("templates/profile/view.html", "r") as f:
    html = f.read()

# Replace skills UI
new_skills_html = """
        <!-- Skills Section -->
        <section class="bg-slate-900 rounded-3xl border border-slate-800 p-8 shadow-xl">
            <div class="flex justify-between items-center border-b border-slate-800 pb-3 mb-6">
                <h2 class="text-sm font-bold uppercase tracking-widest text-indigo-400"><i class="fas fa-tools mr-2"></i> Skills</h2>
                <button onclick="addSkillCategory()" class="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-lg border border-slate-700 transition-colors">
                    <i class="fas fa-plus mr-1"></i> Add Row
                </button>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-left text-sm text-slate-300">
                    <thead class="bg-slate-800/50 uppercase text-xs font-bold text-slate-500">
                        <tr>
                            <th class="px-4 py-3 rounded-tl-lg w-1/4">Category</th>
                            <th class="px-4 py-3 w-2/3">Skills (Comma or Newline separated)</th>
                            <th class="px-4 py-3 rounded-tr-lg w-12 text-center">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="skills-container" class="divide-y divide-slate-800/50"></tbody>
                </table>
            </div>
        </section>
"""
html = re.sub(r'<!-- Skills Section -->.*?</div>\s*</section>', new_skills_html, html, flags=re.DOTALL)

# Replace projects UI
new_projects_html = """
        <!-- Projects Section -->
        <section class="bg-slate-900 rounded-3xl border border-slate-800 p-8 shadow-xl">
            <div class="flex justify-between items-center border-b border-slate-800 pb-3 mb-6">
                <h2 class="text-sm font-bold uppercase tracking-widest text-indigo-400"><i class="fas fa-code-branch mr-2"></i> Projects</h2>
                <button onclick="addProject()" class="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-lg border border-slate-700 transition-colors">
                    <i class="fas fa-plus mr-1"></i> Add Row
                </button>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-left text-sm text-slate-300">
                    <thead class="bg-slate-800/50 uppercase text-xs font-bold text-slate-500">
                        <tr>
                            <th class="px-4 py-3 rounded-tl-lg w-1/5">Project Info</th>
                            <th class="px-4 py-3 w-3/4">Bullets (One per line)</th>
                            <th class="px-4 py-3 rounded-tr-lg w-12 text-center">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="projects-container" class="divide-y divide-slate-800/50"></tbody>
                </table>
            </div>
        </section>
"""
html = re.sub(r'<!-- Projects Section -->.*?</div>\s*</section>', new_projects_html, html, flags=re.DOTALL)

# Replace experience UI
new_exp_html = """
        <!-- Experience Section -->
        <section class="bg-slate-900 rounded-3xl border border-slate-800 p-8 shadow-xl">
            <div class="flex justify-between items-center border-b border-slate-800 pb-3 mb-6">
                <h2 class="text-sm font-bold uppercase tracking-widest text-indigo-400"><i class="fas fa-briefcase mr-2"></i> Experience</h2>
                <button onclick="addExperience()" class="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-lg border border-slate-700 transition-colors">
                    <i class="fas fa-plus mr-1"></i> Add Row
                </button>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-left text-sm text-slate-300">
                    <thead class="bg-slate-800/50 uppercase text-xs font-bold text-slate-500">
                        <tr>
                            <th class="px-4 py-3 rounded-tl-lg w-1/5">Role Info</th>
                            <th class="px-4 py-3 w-3/4">Bullets (One per line)</th>
                            <th class="px-4 py-3 rounded-tr-lg w-12 text-center">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="experience-container" class="divide-y divide-slate-800/50"></tbody>
                </table>
            </div>
        </section>
"""
html = re.sub(r'<!-- Experience Section -->.*?</div>\s*</section>', new_exp_html, html, flags=re.DOTALL)

# Replace education UI
new_edu_html = """
        <!-- Education Section -->
        <section class="bg-slate-900 rounded-3xl border border-slate-800 p-8 shadow-xl">
            <div class="flex justify-between items-center border-b border-slate-800 pb-3 mb-6">
                <h2 class="text-sm font-bold uppercase tracking-widest text-indigo-400"><i class="fas fa-graduation-cap mr-2"></i> Education</h2>
                <button onclick="addEducation()" class="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-lg border border-slate-700 transition-colors">
                    <i class="fas fa-plus mr-1"></i> Add Row
                </button>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-left text-sm text-slate-300">
                    <thead class="bg-slate-800/50 uppercase text-xs font-bold text-slate-500">
                        <tr>
                            <th class="px-4 py-3 rounded-tl-lg">Institution</th>
                            <th class="px-4 py-3">Degree</th>
                            <th class="px-4 py-3">Date</th>
                            <th class="px-4 py-3">Location</th>
                            <th class="px-4 py-3 rounded-tr-lg w-12 text-center">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="education-container" class="divide-y divide-slate-800/50"></tbody>
                </table>
            </div>
        </section>
"""
html = re.sub(r'<!-- Education Section -->.*?</div>\s*</section>', new_edu_html, html, flags=re.DOTALL)


# Now fix JS
js_remove_btn = """
        function createRemoveBtn(parentId) {
            const btn = document.createElement('button');
            btn.innerHTML = '<i class="fas fa-trash-alt"></i>';
            btn.className = 'text-slate-500 hover:text-red-400 transition-colors';
            btn.onclick = () => document.getElementById(parentId).remove();
            return btn;
        }
"""
html = re.sub(r'function createRemoveBtn\(.*?return btn;\s*}', js_remove_btn, html, flags=re.DOTALL)

js_add_exp = """
        function addExperience(data = null) {
            const id = 'exp_' + expCounter++;
            const tr = document.createElement('tr');
            tr.id = id;
            tr.className = 'experience-card hover:bg-slate-800/20 transition-colors';
            
            const bullets = data && data.bullets ? data.bullets.map(b => b.text).join('\\n') : '';

            tr.innerHTML = `
                <td class="px-4 py-4 align-top">
                    <input type="text" class="exp-company w-full bg-slate-900 border border-slate-800 rounded px-3 py-2 text-sm text-indigo-300 font-bold mb-2 placeholder-slate-600" placeholder="Company" value="${data?.company || ''}">
                    <input type="text" class="exp-title w-full bg-slate-900 border border-slate-800 rounded px-3 py-2 text-sm text-white mb-2 placeholder-slate-600" placeholder="Role" value="${data?.title || ''}">
                    <input type="text" class="exp-date w-full bg-slate-900 border border-slate-800 rounded px-3 py-2 text-sm text-slate-400 mb-2 placeholder-slate-600" placeholder="Date Range" value="${data?.date_range || ''}">
                    <input type="text" class="exp-location w-full bg-slate-900 border border-slate-800 rounded px-3 py-2 text-sm text-slate-400 placeholder-slate-600" placeholder="Location" value="${data?.location || ''}">
                </td>
                <td class="px-4 py-4 align-top">
                    <textarea class="exp-bullets w-full bg-slate-900 border border-slate-800 rounded px-4 py-3 text-sm text-white min-h-[140px] resize-y placeholder-slate-600" placeholder="Bullet points...">${bullets}</textarea>
                </td>
                <td class="px-4 py-4 align-middle text-center actions-cell"></td>
            `;
            tr.querySelector('.actions-cell').appendChild(createRemoveBtn(id));
            document.getElementById('experience-container').appendChild(tr);
        }
"""
html = re.sub(r'function addExperience.*?document\.getElementById\(\'experience-container\'\)\.appendChild\(div\);\s*}', js_add_exp, html, flags=re.DOTALL)

js_add_proj = """
        function addProject(data = null) {
            const id = 'proj_' + projCounter++;
            const tr = document.createElement('tr');
            tr.id = id;
            tr.className = 'project-card hover:bg-slate-800/20 transition-colors';
            
            const bullets = data && data.bullets ? data.bullets.map(b => b.text).join('\\n') : '';

            tr.innerHTML = `
                <td class="px-4 py-4 align-top">
                    <input type="text" class="proj-name w-full bg-slate-900 border border-slate-800 rounded px-3 py-2 text-sm text-indigo-300 font-bold mb-2 placeholder-slate-600" placeholder="Project Name" value="${data?.name || ''}">
                    <input type="text" class="proj-role w-full bg-slate-900 border border-slate-800 rounded px-3 py-2 text-sm text-white mb-2 placeholder-slate-600" placeholder="Role" value="${data?.role || ''}">
                    <input type="text" class="proj-date w-full bg-slate-900 border border-slate-800 rounded px-3 py-2 text-sm text-slate-400 mb-2 placeholder-slate-600" placeholder="Date Range" value="${data?.date_range || ''}">
                </td>
                <td class="px-4 py-4 align-top">
                    <textarea class="proj-bullets w-full bg-slate-900 border border-slate-800 rounded px-4 py-3 text-sm text-white min-h-[140px] resize-y placeholder-slate-600" placeholder="Bullet points...">${bullets}</textarea>
                </td>
                <td class="px-4 py-4 align-middle text-center actions-cell"></td>
            `;
            tr.querySelector('.actions-cell').appendChild(createRemoveBtn(id));
            document.getElementById('projects-container').appendChild(tr);
        }
"""
html = re.sub(r'function addProject.*?document\.getElementById\(\'projects-container\'\)\.appendChild\(div\);\s*}', js_add_proj, html, flags=re.DOTALL)

js_add_skill = """
        function addSkillCategory(data = null) {
            const id = 'skill_' + skillCounter++;
            const tr = document.createElement('tr');
            tr.id = id;
            tr.className = 'skill-card hover:bg-slate-800/20 transition-colors';
            
            const itemsStr = data && data.name ? data.name : '';

            tr.innerHTML = `
                <td class="px-4 py-4 align-top">
                    <input type="text" class="skill-category w-full bg-slate-900 border border-slate-800 rounded px-3 py-2 text-sm font-bold text-indigo-300 placeholder-slate-600" placeholder="Category (e.g. Backend)" value="${data?.category || ''}">
                </td>
                <td class="px-4 py-4 align-top">
                    <textarea class="skill-names w-full bg-slate-900 border border-slate-800 rounded px-4 py-3 text-sm text-slate-300 min-h-[80px] resize-y placeholder-slate-600">${itemsStr}</textarea>
                </td>
                <td class="px-4 py-4 align-middle text-center actions-cell"></td>
            `;
            tr.querySelector('.actions-cell').appendChild(createRemoveBtn(id));
            document.getElementById('skills-container').appendChild(tr);
        }
"""
html = re.sub(r'function addSkillCategory.*?document\.getElementById\(\'skills-container\'\)\.appendChild\(div\);\s*}', js_add_skill, html, flags=re.DOTALL)

js_add_edu = """
        function addEducation(data = null) {
            const id = 'edu_' + eduCounter++;
            const tr = document.createElement('tr');
            tr.id = id;
            tr.className = 'edu-card hover:bg-slate-800/20 transition-colors';
            
            tr.innerHTML = `
                <td class="px-4 py-4 align-top">
                    <input type="text" class="edu-school w-full bg-slate-900 border border-slate-800 rounded px-3 py-2 text-sm text-indigo-300 font-bold placeholder-slate-600" placeholder="Institution" value="${data?.institution || ''}">
                </td>
                <td class="px-4 py-4 align-top">
                    <input type="text" class="edu-degree w-full bg-slate-900 border border-slate-800 rounded px-3 py-2 text-sm text-white placeholder-slate-600" placeholder="Degree" value="${data?.degree || ''}">
                </td>
                <td class="px-4 py-4 align-top">
                    <input type="text" class="edu-date w-full bg-slate-900 border border-slate-800 rounded px-3 py-2 text-sm text-slate-400 placeholder-slate-600" placeholder="Date" value="${data?.date_str || ''}">
                </td>
                <td class="px-4 py-4 align-top">
                    <input type="text" class="edu-location w-full bg-slate-900 border border-slate-800 rounded px-3 py-2 text-sm text-slate-400 placeholder-slate-600" placeholder="Location" value="${data?.location || ''}">
                </td>
                <td class="px-4 py-4 align-middle text-center actions-cell"></td>
            `;
            tr.querySelector('.actions-cell').appendChild(createRemoveBtn(id));
            document.getElementById('education-container').appendChild(tr);
        }
"""
html = re.sub(r'function addEducation.*?document\.getElementById\(\'education-container\'\)\.appendChild\(div\);\s*}', js_add_edu, html, flags=re.DOTALL)

# And fix saveProfile
js_save_profile = """
        async function saveProfile() {
            const data = {
                name: document.getElementById('p_name').value,
                headline: document.getElementById('p_headline').value,
                phone: document.getElementById('p_phone').value,
                linkedin_url: document.getElementById('p_linkedin').value,
                github_url: document.getElementById('p_github').value,
                portfolio_url: document.getElementById('p_portfolio').value,
                location: document.getElementById('p_location').value,
                experiences: Array.from(document.querySelectorAll('.experience-card')).map(card => ({
                    company: card.querySelector('.exp-company').value,
                    title: card.querySelector('.exp-title').value,
                    location: card.querySelector('.exp-location').value,
                    date_range: card.querySelector('.exp-date').value,
                    bullets: card.querySelector('.exp-bullets').value.split('\\n').filter(b => b.trim() !== '').map(b => ({text: b.trim()}))
                })),
                projects: Array.from(document.querySelectorAll('.project-card')).map(card => ({
                    name: card.querySelector('.proj-name').value,
                    role: card.querySelector('.proj-role').value,
                    date_range: card.querySelector('.proj-date').value,
                    bullets: card.querySelector('.proj-bullets').value.split('\\n').filter(b => b.trim() !== '').map(b => ({text: b.trim()}))
                })),
                skills: Array.from(document.querySelectorAll('.skill-card')).map(card => ({
                    category: card.querySelector('.skill-category').value,
                    items: card.querySelector('.skill-names').value
                })),
                education: Array.from(document.querySelectorAll('.edu-card')).map(card => ({
                    institution: card.querySelector('.edu-school').value,
                    degree: card.querySelector('.edu-degree').value,
                    date_str: card.querySelector('.edu-date').value,
                    location: card.querySelector('.edu-location').value
                }))
            };
"""
html = re.sub(r'async function saveProfile\(\) \{.*?education: Array\.from\([^}]*\}\)\)\n\s*\};', js_save_profile, html, flags=re.DOTALL)

with open("templates/profile/view.html", "w") as f:
    f.write(html)
print("Rewrote view.html")
