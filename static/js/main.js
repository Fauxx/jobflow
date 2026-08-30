document.addEventListener('DOMContentLoaded', () => {
    let currentJobId = null;
    let ephemeralJobs = [];
    let currentPage = 1;
    const itemsPerPage = 20;

    function renderJobList() {
        const container = document.getElementById('job-list-container');
        const countDisplay = document.getElementById('job-count-display');
        const pagination = document.getElementById('pagination-controls');
        const pageInfo = document.getElementById('page-info');
        
        if (!container) return;
        
        // If we have ephemeral jobs (search mode), clear Jinja templates and render JS
        if (ephemeralJobs.length > 0) {
            container.innerHTML = '';
            countDisplay.innerText = ephemeralJobs.length;
            
            const start = (currentPage - 1) * itemsPerPage;
            const end = start + itemsPerPage;
            const paginatedItems = ephemeralJobs.slice(start, end);
            
            paginatedItems.forEach((job, index) => {
                const realId = 'eph-' + (start + index);
                container.innerHTML += `
                    <div class="bg-gray-800 hover:bg-gray-750 border border-gray-700 p-4 rounded-xl cursor-pointer transition duration-150 hover:border-gray-500 job-card" 
                         id="job-card-${realId}"
                         data-id="${realId}"
                         data-ephemeral="true"
                         data-index="${start + index}"
                         data-title="${escapeHTML(job.title)}"
                         data-company="${escapeHTML(job.company)}"
                         data-location="${escapeHTML(job.location || 'Remote')}"
                         data-url="${escapeHTML(job.source_url || '')}"
                         data-description="${escapeHTML(job.description || '')}"
                         data-source="${escapeHTML(job.source)}">
                        <div class="flex justify-between items-start gap-2 mb-1.5">
                            <h3 class="font-bold text-blue-400 text-sm leading-snug">${escapeHTML(job.title)}</h3>
                            <span class="text-[10px] bg-gray-700 text-gray-300 px-2 py-0.5 rounded font-semibold uppercase tracking-wide shrink-0">${escapeHTML(job.source)}</span>
                        </div>
                        <div class="text-xs text-gray-400 flex flex-col space-y-1 mt-2">
                            <span class="flex items-center"><i class="fa-solid fa-building w-4"></i> ${escapeHTML(job.company)}</span>
                            <span class="flex items-center"><i class="fa-solid fa-location-dot w-4"></i> ${escapeHTML(job.location || 'Remote')}</span>
                        </div>
                    </div>
                `;
            });
            
            // Setup pagination UI
            const totalPages = Math.ceil(ephemeralJobs.length / itemsPerPage);
            if (totalPages > 1) {
                pagination.classList.remove('hidden');
                pageInfo.innerText = `Page ${currentPage} of ${totalPages}`;
            } else {
                pagination.classList.add('hidden');
            }
            
            // Re-bind click events
            bindJobCards();
        }
    }

    function escapeHTML(str) {
        if (!str) return '';
        return str.replace(/[&<>'"]/g, 
            tag => ({
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                "'": '&#39;',
                '"': '&quot;'
            }[tag] || tag)
        );
    }

    // 1. Scraper Form AJAX Intercept
    const scraperForm = document.getElementById('scraper-form');
    if (scraperForm) {
        const keywordsInput = document.getElementById('scrape-keywords');
        const locationInput = document.getElementById('scrape-location');
        const dateSelect = document.getElementById('scrape-date');
        const submitBtn = scraperForm.querySelector('button[type="submit"]');

        if (keywordsInput && localStorage.getItem('scrape-keywords')) keywordsInput.value = localStorage.getItem('scrape-keywords');
        if (locationInput && localStorage.getItem('scrape-location')) locationInput.value = localStorage.getItem('scrape-location');
        if (dateSelect && localStorage.getItem('scrape-date')) dateSelect.value = localStorage.getItem('scrape-date');

        scraperForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            if (keywordsInput) localStorage.setItem('scrape-keywords', keywordsInput.value);
            if (locationInput) localStorage.setItem('scrape-location', locationInput.value);
            if (dateSelect) localStorage.setItem('scrape-date', dateSelect.value);

            const originalText = submitBtn ? submitBtn.innerHTML : 'Scrape';
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Scraping...';
            }

            try {
                const formData = new FormData(scraperForm);
                const response = await fetch('/scrape', { method: 'POST', body: formData });
                
                if (response.ok) {
                    const data = await response.json();
                    ephemeralJobs = data.results.jobs || [];
                    currentPage = 1;
                    
                    // Switch tab to NEW visually if not already
                    window.history.pushState({}, '', '/?status=NEW');
                    
                    renderJobList();
                    
                    // Hide any empty state in the container that Jinja might have left
                    const emptyJinja = document.querySelector('.fa-folder-open');
                    if (emptyJinja) emptyJinja.parentElement.style.display = 'none';

                } else {
                    alert('Scraping failed with status: ' + response.status);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Scraping error.');
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }
            }
        });
    }

    // Pagination controls
    const prevBtn = document.getElementById('prev-page');
    const nextBtn = document.getElementById('next-page');
    if (prevBtn) prevBtn.addEventListener('click', () => {
        if (currentPage > 1) { currentPage--; renderJobList(); }
    });
    if (nextBtn) nextBtn.addEventListener('click', () => {
        const totalPages = Math.ceil(ephemeralJobs.length / itemsPerPage);
        if (currentPage < totalPages) { currentPage++; renderJobList(); }
    });

    // 2. Job Card Selection
    function bindJobCards() {
        const jobCards = document.querySelectorAll('.job-card');
        jobCards.forEach(card => {
            // Remove old listeners to avoid duplicates
            const newCard = card.cloneNode(true);
            card.parentNode.replaceChild(newCard, card);
            
            newCard.addEventListener('click', () => {
                document.querySelectorAll('.job-card').forEach(c => c.classList.remove('border-blue-500', 'bg-gray-750'));
                newCard.classList.add('border-blue-500', 'bg-gray-750');

                const id = newCard.getAttribute('data-id');
                const title = newCard.getAttribute('data-title');
                const company = newCard.getAttribute('data-company');
                const location = newCard.getAttribute('data-location');
                const url = newCard.getAttribute('data-url');
                const description = newCard.getAttribute('data-description');
                const isEphemeral = newCard.getAttribute('data-ephemeral') === 'true';
                
                currentJobId = id;
                window.currentEphemeralIndex = isEphemeral ? newCard.getAttribute('data-index') : null;

                const detailTitle = document.getElementById('detail-title');
                const detailCompany = document.getElementById('detail-company');
                const detailLocation = document.getElementById('detail-location');
                const detailUrlGo = document.getElementById('detail-url-go');
                const detailUrlInput = document.getElementById('detail-url-input');
                const detailLink = document.getElementById('detail-link');
                const detailDescription = document.getElementById('detail-description');
                
                if (detailTitle) detailTitle.innerText = title;
                if (detailCompany) detailCompany.innerText = company;
                if (detailLocation) detailLocation.innerText = location;
                if (detailUrlGo) detailUrlGo.href = url;
                if (detailLink) detailLink.href = url;
                if (detailUrlInput) detailUrlInput.value = url;
                if (detailDescription) detailDescription.innerHTML = description;

                const detailPanel = document.getElementById('job-detail-content');
                const emptyState = document.getElementById('no-job-selected');
                if (detailPanel) detailPanel.classList.remove('hidden');
                if (emptyState) emptyState.classList.add('hidden');

                // Adjust status forms based on ephemeral state
                const approveForm = document.getElementById('approve-form');
                const approveBtn = approveForm ? approveForm.querySelector('button') : null;
                
                if (isEphemeral) {
                    if (approveForm) {
                        approveForm.onsubmit = async (e) => {
                            e.preventDefault();
                            if(approveBtn) approveBtn.innerHTML = "Saving...";
                            
                            const jobData = ephemeralJobs[window.currentEphemeralIndex];
                            try {
                                const resp = await fetch('/jobs/save', {
                                    method: 'POST',
                                    headers: {'Content-Type': 'application/json'},
                                    body: JSON.stringify(jobData)
                                });
                                if(resp.ok) {
                                    alert("Saved to Database!");
                                    // Remove from ephemeral list
                                    ephemeralJobs.splice(window.currentEphemeralIndex, 1);
                                    renderJobList();
                                    detailPanel.classList.add('hidden');
                                    emptyState.classList.remove('hidden');
                                }
                            } catch (e) {
                                console.error(e);
                                alert("Save failed.");
                            }
                        };
                    }
                } else {
                    // Standard POST to status endpoint
                    if (approveForm) {
                        approveForm.onsubmit = null;
                        approveForm.action = `/jobs/${id}/status`;
                    }
                    const applyForm = document.getElementById('apply-form');
                    if (applyForm) applyForm.action = `/jobs/${id}/status`;
                }

                // Reset AI
                const formBody = document.getElementById('form-body');
                const bulletsList = document.getElementById('bullets-list');
                const qaList = document.getElementById('qa-list');
                if (formBody) formBody.value = `Dear Hiring Team,\n\nI am writing to apply for the ${title} position at ${company}.\n\nBest regards,`;
                if (bulletsList) bulletsList.innerHTML = `<p class="text-center py-6 text-xs text-gray-500">Click "Tailor Now" to load optimizations.</p>`;
                if (qaList) qaList.innerHTML = `<p class="text-center py-6 text-xs text-gray-500">Click "Tailor Now" to load screening answers.</p>`;
            });
        });
    }

    // 3. AI Tailoring Logic
    window.tailorAll = async function() {
        if (!currentJobId) return;
        if (window.currentEphemeralIndex !== null && window.currentEphemeralIndex !== undefined) {
            alert("Please 'Approve' and save this job to your database first before tailoring!");
            return;
        }

        const btn = document.getElementById('tailor-btn');
        if (!btn) return;

        const originalHTML = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = `<i class="fa-solid fa-spinner animate-spin"></i> <span>Tailoring...</span>`;

        try {
            const response = await fetch(`/jobs/${currentJobId}/tailor`);
            if (response.ok) {
                const data = await response.json();
                const formBody = document.getElementById('form-body');
                if (formBody && data.body) formBody.value = data.body;
                
                const qaContainer = document.getElementById('qa-list');
                if (qaContainer) {
                    qaContainer.innerHTML = '';
                    if (data.screening_answers && Object.keys(data.screening_answers).length > 0) {
                        for (const [q, a] of Object.entries(data.screening_answers)) {
                            qaContainer.innerHTML += `
                                <div class="mb-4 bg-gray-800 p-3 rounded border border-gray-700">
                                    <p class="font-bold text-xs text-blue-300 mb-1">Q: ${q}</p>
                                    <p class="text-xs text-gray-300">A: ${a}</p>
                                </div>`;
                        }
                    } else {
                        qaContainer.innerHTML = `<p class="text-center py-6 text-xs text-gray-500">No QA generated.</p>`;
                    }
                }
            }
        } catch (e) {
            console.error(e);
            alert("Failed to tailor assets.");
        } finally {
            btn.disabled = false;
            btn.innerHTML = originalHTML;
        }
    };

    // 4. Tab Switching
    window.switchTab = function(activeTabId) {
        ['tab-cover', 'tab-bullets', 'tab-qa'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.classList.add('hidden');
        });
        
        const activeTab = document.getElementById(activeTabId);
        if (activeTab) activeTab.classList.remove('hidden');

        ['btn-tab-cover', 'btn-tab-bullets', 'btn-tab-qa'].forEach(id => {
            const btn = document.getElementById(id);
            if (btn) {
                btn.classList.remove('active-tab-btn', 'text-white', 'border-blue-500');
                btn.classList.add('text-gray-500', 'border-transparent');
            }
        });

        const activeBtn = document.getElementById(`btn-${activeTabId}`);
        if (activeBtn) {
            activeBtn.classList.remove('text-gray-500', 'border-transparent');
            activeBtn.classList.add('active-tab-btn', 'text-white', 'border-blue-500');
        }
    };

    window.copyToClipboard = function(elementId) {
        const el = document.getElementById(elementId);
        if (!el) return;
        
        let text = el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' ? el.value : el.innerText;
        navigator.clipboard.writeText(text).then(() => {
            alert('Copied to clipboard!');
        }).catch(err => {
            console.error('Copy failed', err);
        });
    };

    // Initial bind for Jinja-rendered cards (Approved/Skipped tabs)
    bindJobCards();
});
