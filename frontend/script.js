document.addEventListener('DOMContentLoaded', function() {
    // Initialize Materialize components
    M.AutoInit();

    // --- Element Selectors ---
    const analyzeButton = document.getElementById('analyze_button');
    const leetcodeUrlInput = document.getElementById('leetcode_url');
    const mainLoader = document.getElementById('main_loader');
    const resultsContainer = document.getElementById('results_container');

    // Content containers
    const analysisContent = document.getElementById('analysis_content');
    const explanationContent = document.getElementById('explanation_content');
    const solutionsContainer = document.querySelectorAll('.card-content .row')[0];
    const solutionContentPython = document.getElementById('solution_content_python');
    const solutionContentJava = document.getElementById('solution_content_java');
    const solutionContentCpp = document.getElementById('solution_content_cpp');
    const resourcesList = document.getElementById('resources_list');
    const similarProblemsContainer = document.querySelectorAll('.card-content .row')[1];
    const easyProblemsContainer = document.getElementById('easy_problems_tab');
    const mediumProblemsContainer = document.getElementById('medium_problems_tab');
    const hardProblemsContainer = document.getElementById('hard_problems_tab');

    // Chat widget elements
    const chatWidget = document.getElementById('chat_widget');
    const chatContainer = document.getElementById('chat_container');
    const chatHistory = document.getElementById('chat_history');
    const chatInput = document.getElementById('chat_input');
    const chatSendButton = document.getElementById('chat_send_button');
    const chatLoading = document.getElementById('chat_loading');
    const minimizeChatButton = document.getElementById('minimize_chat');
    const maximizeChatButton = document.getElementById('maximize_chat');

    const API_BASE_URL = 'http://127.0.0.1:8000';
    let currentScrapedProblem = null; // Store the scraped problem data globally
    let currentChatHistory = [];

    // --- Main Handler ---
    analyzeButton.addEventListener('click', async () => {
        const url = leetcodeUrlInput.value.trim();
        if (!url) {
            M.toast({ html: 'Please enter a LeetCode URL' });
            return;
        }

        clearResults();
        resultsContainer.style.display = 'block';
        setLoaders(true);

        try {
            currentScrapedProblem = await fetchScrapedProblem(url);
            mainLoader.style.display = 'none';
            
            fetchAllSections(currentScrapedProblem);
            chatWidget.style.display = 'flex';

        } catch (error) {
            console.error('Error during analysis:', error);
            M.toast({ html: `An error occurred: ${error.message}` });
            mainLoader.style.display = 'none';
            resultsContainer.style.display = 'none';
        }
    });

    // --- Retry Icon Handler ---
    resultsContainer.addEventListener('click', (e) => {
        if (e.target.classList.contains('retry-icon')) {
            const endpoint = e.target.dataset.endpoint;
            if (endpoint && currentScrapedProblem) {
                const cardContent = e.target.closest('.card-content');
                const loader = cardContent.querySelector('.loader');
                const target = cardContent.querySelector('div[id]');
                
                fetchAndDisplay({
                    endpoint: endpoint,
                    body: { problem: currentScrapedProblem },
                    target: target,
                    loader: loader,
                    retryIcon: e.target
                });
            }
        }
    });

    // --- Data Fetching Functions ---

    async function fetchScrapedProblem(url) {
        mainLoader.style.display = 'block';
        const response = await fetch(`${API_BASE_URL}/api/scrape`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Failed to scrape problem data.');
        }
        return response.json();
    }

    function fetchAllSections(problem) {
        const requestBody = { problem };
        const sections = [
            { endpoint: 'analysis', target: analysisContent },
            { endpoint: 'explanation', target: explanationContent },
            { endpoint: 'solutions', target: solutionsContainer },
            { endpoint: 'resources', target: resourcesList },
            { endpoint: 'similar-problems', target: similarProblemsContainer }
        ];

        sections.forEach(section => {
            const cardContent = section.target.closest('.card-content');
            const loader = cardContent.querySelector('.loader');
            const retryIcon = cardContent.querySelector('.retry-icon');
            fetchAndDisplay({ ...section, body: requestBody, loader, retryIcon });
        });
    }

    async function fetchAndDisplay({ endpoint, body, target, loader, retryIcon }) {
        // Reset section state
        loader.style.display = 'block';
        target.style.display = 'none';
        // For containers that have sub-containers, we don't wipe the whole thing.
        if (endpoint !== 'similar-problems' && endpoint !== 'solutions') {
            target.innerHTML = '';
        }
        retryIcon.style.display = 'none';

        try {
            const response = await fetch(`${API_BASE_URL}/api/${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();
            const success = displaySection(endpoint, data, target);

            if (!success) {
                throw new Error('Invalid or empty data received from server.');
            }

        } catch (error) {
            console.error(`Error fetching ${endpoint}:`, error);
            target.innerHTML = `<p class="red-text center-align">Failed to load. Click to retry.</p>`;
            retryIcon.style.display = 'inline-block';
        } finally {
            loader.style.display = 'none';
            target.style.display = 'block';
        }
    }

    // --- UI Display Functions ---

    function clearResults() {
        const contentAreas = [analysisContent, explanationContent, resourcesList, easyProblemsContainer, mediumProblemsContainer, hardProblemsContainer];
        contentAreas.forEach(el => {
            el.innerHTML = '';
        });
        solutionContentPython.textContent = '';
        solutionContentJava.textContent = '';
        solutionContentCpp.textContent = '';

        resultsContainer.style.display = 'none';
        document.querySelectorAll('.retry-icon').forEach(icon => icon.style.display = 'none');
        chatHistory.innerHTML = '';
        chatWidget.style.display = 'none';
        currentScrapedProblem = null;
    }

    function setLoaders(isLoading) {
        const loaders = document.querySelectorAll('.loader');
        loaders.forEach(loader => {
            loader.innerHTML = isLoading ? '<div class="preloader-wrapper small active"><div class="spinner-layer spinner-green-only"><div class="circle-clipper left"><div class="circle"></div></div><div class="gap-patch"><div class="circle"></div></div><div class="circle-clipper right"><div class="circle"></div></div></div></div>' : '';
            loader.style.display = isLoading ? 'block' : 'none';
        });
    }

    function displaySection(endpoint, data, target) {
        if (endpoint !== 'solutions' && endpoint !== 'similar-problems') {
            target.innerHTML = ''; // Clear previous content only for non-container sections
        }
        switch (endpoint) {
            case 'analysis':
                if (!data.analysis) return false;
                target.innerHTML = `<p>${data.analysis.replace(/\n/g, '<br>')}</p>`;
                return true;
            case 'explanation':
                if (!data.explanation) return false;
                target.innerHTML = formatExplanation(data.explanation);
                return true;
            case 'solutions':
                if (!data.solution || !data.solution.python) return false;
                solutionContentPython.textContent = data.solution.python;
                solutionContentJava.textContent = data.solution.java;
                solutionContentCpp.textContent = data.solution.cpp;
                // Initialize tabs
                const solutionsTabs = document.querySelectorAll('.card-content .tabs')[0];
                M.Tabs.init(solutionsTabs);
                return true;
            case 'resources':
                if (!data.resources || data.resources.length === 0) return false;
                data.resources.forEach(resource => {
                    const li = document.createElement('li');
                    li.className = 'collection-item';
                    li.innerHTML = `
                        <div>
                            <a href="${resource.url}" target="_blank">${resource.title}</a>
                            <p style="font-size: 0.9rem; color: #666;">${resource.reason}</p>
                        </div>`;
                    target.appendChild(li);
                });
                return true;
            case 'similar-problems':
                if (!data.similar_problems) return false;
                populateSimilarProblems(data.similar_problems.easy, easyProblemsContainer);
                populateSimilarProblems(data.similar_problems.medium, mediumProblemsContainer);
                populateSimilarProblems(data.similar_problems.hard, hardProblemsContainer);
                // Initialize tabs
                const similarProblemsTabs = document.querySelectorAll('.card-content .tabs')[1];
                M.Tabs.init(similarProblemsTabs);
                return true;
        }
        return false;
    }

    function populateSimilarProblems(problems, container) {
        container.innerHTML = '';
        if (!problems || problems.length === 0) {
            container.innerHTML = '<p class="center-align" style="padding-top: 10px;">No problems found.</p>';
            return;
        }
        problems.forEach(problem => {
            const item = document.createElement('a');
            item.href = problem.url;
            item.target = '_blank';
            item.className = 'collection-item';
            item.innerHTML = `
                <strong>${problem.title}</strong>
                <p style="font-size: 0.9rem; color: #666;">${problem.reason}</p>
            `;
            container.appendChild(item);
        });
    }

    function formatExplanation(text) {
        return marked.parse(text);
    }

    // --- Chat Handlers ---
    const handleSendMessage = async () => {
        const message = chatInput.value.trim();
        if (!message || !currentScrapedProblem) return;

        appendMessage(message, 'user');
        chatInput.value = '';
        chatLoading.style.display = 'flex';

        try {
            const response = await fetch(`${API_BASE_URL}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    problem_context: currentScrapedProblem.description,
                    chat_history: currentChatHistory,
                    user_message: message
                })
            });
            if (!response.ok) throw new Error('Chat API request failed.');
            const data = await response.json();
            appendMessage(data.llm_reply, 'llm');
        } catch (error) {
            console.error('Error in chat:', error);
            M.toast({ html: 'Chat error. Check console.' });
        } finally {
            chatLoading.style.display = 'none';
        }
    };

    chatSendButton.addEventListener('click', handleSendMessage);
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleSendMessage();
        }
    });

    function appendMessage(message, sender) {
        const messageWrapper = document.createElement('div');
        messageWrapper.className = sender === 'user' ? 'user-message' : 'llm-message';
        const messageBubble = document.createElement('div');
        messageBubble.className = 'message-bubble';
        messageBubble.textContent = message;
        messageWrapper.appendChild(messageBubble);
        chatHistory.appendChild(messageWrapper);
        chatHistory.scrollTop = chatHistory.scrollHeight;
        currentChatHistory.push({ role: sender, content: message });
    }

    // --- Chat Widget UI Handlers ---
    minimizeChatButton.addEventListener('click', () => {
        chatContainer.style.display = 'none';
        minimizeChatButton.style.display = 'none';
        maximizeChatButton.style.display = 'inline-block';
        chatWidget.classList.remove('maximized');
    });

    maximizeChatButton.addEventListener('click', () => {
        chatContainer.style.display = 'flex';
        minimizeChatButton.style.display = 'inline-block';
        maximizeChatButton.style.display = 'none';
    });

    document.querySelector('.chat-header').addEventListener('dblclick', () => {
        chatWidget.classList.toggle('maximized');
    });
const mainTabs = document.querySelector('#results_container .tabs');
    M.Tabs.init(mainTabs);
});
