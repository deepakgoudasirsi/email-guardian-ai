// DOM Elements
const authButton = document.getElementById('authButton');
const emailList = document.getElementById('emailList');
const analysisResults = document.getElementById('analysisResults');
const loadingOverlay = document.getElementById('loadingOverlay');

// Show loading overlay
function showLoading() {
    loadingOverlay.classList.remove('hidden');
}

// Hide loading overlay
function hideLoading() {
    loadingOverlay.classList.add('hidden');
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Get risk score class
function getRiskScoreClass(score) {
    if (score >= 0.7) return 'risk-high';
    if (score >= 0.4) return 'risk-medium';
    return 'risk-low';
}

// Create email item element
function createEmailItem(email) {
    const div = document.createElement('div');
    div.className = 'email-item bg-white p-4 rounded-lg shadow flex items-center justify-between';
    div.innerHTML = `
        <div class="flex-1">
            <h3 class="font-semibold">${email.subject}</h3>
            <p class="text-gray-600">From: ${email.sender}</p>
            <p class="text-sm text-gray-500">${formatDate(email.date)}</p>
        </div>
        <button class="analyze-btn bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded ml-4"
                data-email-id="${email.id}">
            Analyze
        </button>
    `;
    return div;
}

// Create analysis result element
function createAnalysisResult(result) {
    const div = document.createElement('div');
    div.className = `analysis-card bg-white p-4 rounded-lg shadow mb-4 ${
        result.is_phishing ? 'danger' : result.risk_score >= 0.4 ? 'warning' : 'safe'
    }`;
    div.innerHTML = `
        <div class="flex items-center justify-between mb-2">
            <h3 class="font-semibold">${result.subject}</h3>
            <div class="risk-score ${getRiskScoreClass(result.risk_score)}">
                ${Math.round(result.risk_score * 100)}%
            </div>
        </div>
        <p class="text-gray-600 mb-2">From: ${result.sender}</p>
        <div class="analysis-content text-gray-700 mb-2">
            ${result.analysis}
        </div>
        <div class="recommendations bg-gray-50 p-3 rounded">
            <h4 class="font-semibold mb-1">Recommendations:</h4>
            <p>${result.recommendations}</p>
        </div>
    `;
    return div;
}

// Handle Gmail authentication
async function handleAuth() {
    try {
        showLoading();
        const response = await fetch('/auth/gmail');
        if (response.redirected) {
            window.location.href = response.url;
        }
    } catch (error) {
        console.error('Authentication error:', error);
        alert('Failed to authenticate with Gmail');
    } finally {
        hideLoading();
    }
}

// Load emails from Gmail
async function loadEmails() {
    try {
        showLoading();
        const response = await fetch('/api/emails');
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        displayEmails(data.emails);
    } catch (error) {
        console.error('Error loading emails:', error);
        if (error.message.includes('Authentication')) {
            // Show connect button if not authenticated
            document.getElementById('authButton').style.display = 'block';
        } else {
            alert('Failed to load emails. Please try again.');
        }
    } finally {
        hideLoading();
    }
}

// Display emails in the UI
function displayEmails(emails) {
    const emailList = document.getElementById('emailList');
    emailList.innerHTML = '';
    
    if (!emails || emails.length === 0) {
        emailList.innerHTML = '<div class="text-center p-4">No emails found</div>';
        return;
    }
    
    emails.forEach(email => {
        const emailElement = createEmailElement(email);
        emailList.appendChild(emailElement);
    });
}

// Create email element
function createEmailElement(email) {
    const div = document.createElement('div');
    div.className = 'bg-white rounded-lg shadow p-4 mb-4 hover:shadow-lg transition-shadow';
    div.innerHTML = `
        <div class="flex justify-between items-start">
            <div>
                <h3 class="font-semibold text-lg">${email.subject || 'No Subject'}</h3>
                <p class="text-gray-600">From: ${email.sender}</p>
                <p class="text-gray-500 text-sm">${email.date}</p>
            </div>
            <button onclick="analyzeEmail('${email.id}')" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                Analyze
            </button>
        </div>
    `;
    return div;
}

// Analyze a specific email
async function analyzeEmail(emailId) {
    try {
        showLoading();
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email_ids: [emailId] })
        });
        
        const data = await response.json();
        if (data.error) {
            throw new Error(data.error);
        }
        
        displayAnalysis(data.results[0]);
    } catch (error) {
        console.error('Error analyzing email:', error);
        alert('Failed to analyze email. Please try again.');
    } finally {
        hideLoading();
    }
}

// Display analysis results
function displayAnalysis(analysis) {
    const modal = document.getElementById('analysisModal');
    const content = document.getElementById('analysisContent');
    
    content.innerHTML = `
        <div class="p-4">
            <h2 class="text-xl font-bold mb-4">Analysis Results</h2>
            <div class="mb-4">
                <p class="font-semibold">Risk Score: ${analysis.risk_score}</p>
                <p class="font-semibold">Risk Level: ${analysis.risk_level}</p>
            </div>
            <div class="mb-4">
                <h3 class="font-semibold mb-2">Findings:</h3>
                <ul class="list-disc pl-5">
                    ${analysis.findings.map(finding => `<li>${finding}</li>`).join('')}
                </ul>
            </div>
            <div>
                <h3 class="font-semibold mb-2">Recommendation:</h3>
                <p>${analysis.recommendation}</p>
            </div>
        </div>
    `;
    
    modal.style.display = 'block';
}

// Show loading indicator
function showLoading() {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.style.display = 'block';
    }
}

// Hide loading indicator
function hideLoading() {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.style.display = 'none';
    }
}

// Close modal
function closeModal() {
    const modal = document.getElementById('analysisModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Check if we're returning from OAuth
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('code')) {
        handleAuthCallback(urlParams.get('code'));
    } else {
        loadEmails();
    }
});

// Handle OAuth callback
async function handleAuthCallback(code) {
    try {
        showLoading();
        const response = await fetch(`/oauth2callback?code=${code}`);
        if (response.redirected) {
            window.location.href = response.url;
        }
    } catch (error) {
        console.error('Auth callback error:', error);
        alert('Failed to complete authentication');
    } finally {
        hideLoading();
    }
} 