const sectors = [
  {
    name: 'Banking',
    description: 'This section surveys banks licensed by the Bank of Ghana.',
    organizations: ['ABSA BANK', 'GCB BANK', 'STANDARD CHARTERED BANK', 'ZENITH BANK']
  },
  {
    name: 'Healthcare',
    description: 'This section surveys both public and private healthcare facilities.',
    organizations: ['Korle Bu Teaching Hospital', 'Ridge Hospital', 'MediCare Plus', 'LifeCare Clinic']
  },
  {
    name: 'Hospitality',
    description: 'This section surveys hotels that are regulated by the Ghana Tourism Authority.',
    organizations: ['Movenpick Ambassador Hotel', 'Labadi Beach Hotel', 'Accra City Hotel', 'The Royal Hotel']
  },
  {
    name: 'Telecommunications',
    description: 'This section surveys licensed telecom companies in Ghana.',
    organizations: ['MTN Ghana', 'Telecel Ghana', 'AT Ghana', 'Vodafone Ghana']
  },
  {
    name: 'Retail Malls',
    description: 'This section surveys major retail outlets and shopping malls in Ghana.',
    organizations: ['Accra Mall', 'West Hills Mall', 'A&C Mall', 'The Junction']
  },
  {
    name: 'Public Institutions',
    description: 'This section surveys public sector institutions in Ghana.',
    organizations: ['Ghana Immigration Service', 'Ghana Revenue Authority', 'National Identification Authority', 'Ghana Post']
  },
  {
    name: 'Online Businesses',
    description: 'This section surveys popular e-commerce businesses in Ghana.',
    organizations: ['Jumia Ghana', 'Konga', 'Glovo Ghana', 'Shopaholic']
  },
  {
    name: 'Transportation',
    description: 'This section surveys ride-hailing and transport services in Ghana.',
    organizations: ['Uber', 'Bolt', 'Yango', 'Mogo']
  },
  {
    name: 'Insurance',
    description: 'This section surveys insurance companies regulated by the National Insurance Commission.',
    organizations: ['Ghana Union Assurance', 'SIC Insurance', 'Enterprise Insurance', 'NIA Insurance']
  },
  {
    name: 'Utilities',
    description: 'This section surveys utilities, including Zoomlion and other service providers.',
    organizations: ['Electricity Company of Ghana', 'Water Company', 'Zoomlion Ghana', 'National Petroleum Authority']
  },
  {
    name: 'Oil Marketing Companies',
    description: 'This section surveys oil marketing companies in Ghana.',
    organizations: ['GOIL', 'Shell', 'TotalEnergies', 'PetroSA']
  }
];

const steps = [
  {
    id: 'intro',
    title: 'SECTORS OF ORGANIZATIONS',
    copy: 'A minimum number of 30 responses is required for an organization to be featured in the ranking or report, and one can complete the survey for as many sectors as possible. A minimum of five (5) is, however, recommended.',
    type: 'intro'
  },
  {
    id: 'sector',
    title: 'Select the sector you want to evaluate',
    copy: 'Choose the sector that best matches the service experience you wish to share.',
    type: 'sector'
  },
  {
    id: 'organization',
    title: 'Select your organization',
    copy: 'Choose the organization or provider you dealt with most recently.',
    type: 'organization'
  },
  {
    id: 'satisfaction',
    title: 'Overall satisfaction',
    copy: 'How satisfied were you with the service you received?',
    type: 'scale'
  },
  {
    id: 'dimensions',
    title: 'Which dimensions mattered most?',
    copy: 'Select the service qualities that most influenced your experience.',
    type: 'checkboxes'
  },
  {
    id: 'channel',
    title: 'How did you interact with the provider?',
    copy: 'Choose the main channels you used.',
    type: 'channel'
  },
  {
    id: 'demographics',
    title: 'Demographics',
    copy: 'These questions help us understand the broader customer profile.',
    type: 'demographics'
  },
  {
    id: 'review',
    title: 'Review your answers',
    copy: 'Double-check your responses before submitting.',
    type: 'review'
  }
];

const state = {
  currentStep: 0,
  answers: JSON.parse(localStorage.getItem('gcsi-survey') || '{}'),
  errors: {},
  isLoading: false,
  submitted: false,
  submissionMessage: ''
};

const contentEl = document.getElementById('surveyContent');
const progressEl = document.getElementById('progressBar');

function init() {
  render();
}

function render() {
  const step = steps[state.currentStep];
  const progress = ((state.currentStep + 1) / steps.length) * 100;
  progressEl.innerHTML = `<span style="width:${progress}%"></span>`;

  if (state.submitted) {
    renderSuccess();
    return;
  }

  if (state.isLoading) {
    contentEl.innerHTML = `
      <div class="hero">
        <h2>Submitting your response</h2>
        <p class="step-copy">Please wait while your survey is being sent to our secure endpoint.</p>
        <div class="success-box">Thank you for contributing your feedback.</div>
      </div>
    `;
    return;
  }

  const stepMarkup = buildStep(step);
  contentEl.innerHTML = stepMarkup;
}

function buildStep(step) {
  if (step.type === 'intro') {
    return `
      <div class="hero">
        <h2>${step.title}</h2>
        <p class="step-copy">${step.copy}</p>
        <div class="card-grid">
          ${sectors.map((sector) => `
            <div class="option-card">
              <strong>${sector.name}</strong>
              <div class="step-copy">${sector.description}</div>
            </div>
          `).join('')}
        </div>
        <div class="actions">
          <div></div>
          <button class="btn-primary" onclick="nextStep()">Start survey</button>
        </div>
      </div>
    `;
  }

  if (step.type === 'sector') {
    return `
      <div class="hero">
        <h2>${step.title}</h2>
        <p class="step-copy">${step.copy}</p>
        <div class="card-grid">
          ${sectors.map((sector) => `
            <div class="option-card ${state.answers.sector === sector.name ? 'selected' : ''}" onclick="selectSector('${sector.name}')">
              <strong>${sector.name}</strong>
              <div class="step-copy">${sector.description}</div>
            </div>
          `).join('')}
        </div>
        ${renderError('sector')}
        <div class="actions">
          <button class="btn-secondary" onclick="prevStep()">Back</button>
          <button class="btn-primary" onclick="nextStep()">Continue</button>
        </div>
      </div>
    `;
  }

  if (step.type === 'organization') {
    const sector = sectors.find((item) => item.name === state.answers.sector) || sectors[0];
    const orgs = sector.organizations;
    return `
      <div class="hero">
        <h2>${step.title}</h2>
        <p class="step-copy">${step.copy}</p>
        <div class="field-list">
          <div class="field-group">
            <label for="organization">Organization</label>
            <select id="organization" onchange="setAnswer('organization', this.value)">
              <option value="">Choose an organization</option>
              ${orgs.map((org) => `<option value="${org}" ${state.answers.organization === org ? 'selected' : ''}>${org}</option>`).join('')}
            </select>
          </div>
        </div>
        ${renderError('organization')}
        <div class="actions">
          <button class="btn-secondary" onclick="prevStep()">Back</button>
          <button class="btn-primary" onclick="nextStep()">Continue</button>
        </div>
      </div>
    `;
  }

  if (step.type === 'scale') {
    const scaleOptions = [
      { value: 1, label: '1' },
      { value: 2, label: '2' },
      { value: 3, label: '3' },
      { value: 4, label: '4' },
      { value: 5, label: '5' },
      { value: 6, label: '6' },
      { value: 7, label: '7' }
    ];
    return `
      <div class="hero">
        <h2>${step.title}</h2>
        <p class="step-copy">${step.copy}</p>
        <div class="scale-list">
          ${scaleOptions.map((option) => `
            <div class="scale-chip ${state.answers.satisfaction === String(option.value) ? 'selected' : ''}" onclick="setAnswer('satisfaction', '${option.value}')">
              ${option.label}
            </div>
          `).join('')}
        </div>
        ${renderError('satisfaction')}
        <div class="actions">
          <button class="btn-secondary" onclick="prevStep()">Back</button>
          <button class="btn-primary" onclick="nextStep()">Continue</button>
        </div>
      </div>
    `;
  }

  if (step.type === 'checkboxes') {
    const options = [
      'Reliability',
      'Professionalism',
      'Look and feel',
      'Ease of doing business',
      'Communication',
      'Complaint handling'
    ];
    const selected = state.answers.dimensions || [];
    return `
      <div class="hero">
        <h2>${step.title}</h2>
        <p class="step-copy">${step.copy}</p>
        <div class="checkbox-list">
          ${options.map((option) => `
            <label class="check-item">
              <input type="checkbox" value="${option}" ${selected.includes(option) ? 'checked' : ''} onchange="toggleDimension('${option}', this.checked)" />
              <span>${option}</span>
            </label>
          `).join('')}
        </div>
        ${renderError('dimensions')}
        <div class="actions">
          <button class="btn-secondary" onclick="prevStep()">Back</button>
          <button class="btn-primary" onclick="nextStep()">Continue</button>
        </div>
      </div>
    `;
  }

  if (step.type === 'channel') {
    const options = ['In person', 'Phone', 'Mobile app', 'Social media', 'Website', 'Email'];
    const selected = state.answers.channels || [];
    return `
      <div class="hero">
        <h2>${step.title}</h2>
        <p class="step-copy">${step.copy}</p>
        <div class="checkbox-list">
          ${options.map((option) => `
            <label class="check-item">
              <input type="checkbox" value="${option}" ${selected.includes(option) ? 'checked' : ''} onchange="toggleChannel('${option}', this.checked)" />
              <span>${option}</span>
            </label>
          `).join('')}
        </div>
        ${renderError('channels')}
        <div class="actions">
          <button class="btn-secondary" onclick="prevStep()">Back</button>
          <button class="btn-primary" onclick="nextStep()">Continue</button>
        </div>
      </div>
    `;
  }

  if (step.type === 'demographics') {
    return `
      <div class="hero">
        <h2>${step.title}</h2>
        <p class="step-copy">${step.copy}</p>
        <div class="field-list">
          <div class="field-group">
            <label for="gender">Gender</label>
            <select id="gender" onchange="setAnswer('gender', this.value)">
              <option value="">Choose</option>
              <option value="Female" ${state.answers.gender === 'Female' ? 'selected' : ''}>Female</option>
              <option value="Male" ${state.answers.gender === 'Male' ? 'selected' : ''}>Male</option>
              <option value="Prefer not to say" ${state.answers.gender === 'Prefer not to say' ? 'selected' : ''}>Prefer not to say</option>
            </select>
          </div>
          <div class="field-group">
            <label for="age">Age group</label>
            <select id="age" onchange="setAnswer('age', this.value)">
              <option value="">Choose</option>
              <option value="18-24" ${state.answers.age === '18-24' ? 'selected' : ''}>18-24</option>
              <option value="25-34" ${state.answers.age === '25-34' ? 'selected' : ''}>25-34</option>
              <option value="35-44" ${state.answers.age === '35-44' ? 'selected' : ''}>35-44</option>
              <option value="45+" ${state.answers.age === '45+' ? 'selected' : ''}>45+</option>
            </select>
          </div>
          <div class="field-group">
            <label for="region">Region</label>
            <input id="region" type="text" value="${state.answers.region || ''}" oninput="setAnswer('region', this.value)" placeholder="e.g. Greater Accra" />
          </div>
          <div class="field-group">
            <label for="education">Highest education</label>
            <input id="education" type="text" value="${state.answers.education || ''}" oninput="setAnswer('education', this.value)" placeholder="e.g. Bachelor's degree" />
          </div>
        </div>
        ${renderError('demographics')}
        <div class="actions">
          <button class="btn-secondary" onclick="prevStep()">Back</button>
          <button class="btn-primary" onclick="nextStep()">Review answers</button>
        </div>
      </div>
    `;
  }

  if (step.type === 'review') {
    return `
      <div class="hero">
        <h2>${step.title}</h2>
        <p class="step-copy">${step.copy}</p>
        <div class="summary-card">
          <h3>Summary</h3>
          <div class="summary-item"><span>Sector</span><strong>${state.answers.sector || 'Not selected'}</strong></div>
          <div class="summary-item"><span>Organization</span><strong>${state.answers.organization || 'Not selected'}</strong></div>
          <div class="summary-item"><span>Overall satisfaction</span><strong>${state.answers.satisfaction || 'Not selected'}</strong></div>
          <div class="summary-item"><span>Dimensions</span><strong>${(state.answers.dimensions || []).join(', ') || 'None selected'}</strong></div>
          <div class="summary-item"><span>Channels</span><strong>${(state.answers.channels || []).join(', ') || 'None selected'}</strong></div>
          <div class="summary-item"><span>Demographics</span><strong>${state.answers.gender || ''} • ${state.answers.age || ''} • ${state.answers.region || ''}</strong></div>
        </div>
        <div class="actions">
          <button class="btn-secondary" onclick="prevStep()">Back</button>
          <button class="btn-primary" onclick="submitSurvey()">Submit survey</button>
        </div>
      </div>
    `;
  }

  return '';
}

function renderError(field) {
  if (!state.errors[field]) return '';
  return `<div class="error-text">${state.errors[field]}</div>`;
}

function renderSuccess() {
  contentEl.innerHTML = `
    <div class="hero">
      <h2>Survey completed</h2>
      <p class="step-copy">Thank you for taking part in the Ghana Customer Service Index Survey 2024. Your feedback has been recorded.</p>
      <div class="success-box">${state.submissionMessage || 'Thank you for sharing your experience.'}</div>
      <div class="actions">
        <button class="btn-primary" onclick="resetSurvey()">Start again</button>
      </div>
    </div>
  `;
}

function validateCurrentStep() {
  state.errors = {};
  const step = steps[state.currentStep];
  if (step.type === 'sector' && !state.answers.sector) {
    state.errors.sector = 'Please select a sector to continue.';
  }
  if (step.type === 'organization' && !state.answers.organization) {
    state.errors.organization = 'Please choose an organization.';
  }
  if (step.type === 'scale' && !state.answers.satisfaction) {
    state.errors.satisfaction = 'Please choose a satisfaction score.';
  }
  if (step.type === 'checkboxes' && (!state.answers.dimensions || state.answers.dimensions.length === 0)) {
    state.errors.dimensions = 'Choose at least one dimension.';
  }
  if (step.type === 'channel' && (!state.answers.channels || state.answers.channels.length === 0)) {
    state.errors.channels = 'Choose at least one channel.';
  }
  if (step.type === 'demographics' && (!state.answers.gender || !state.answers.age || !state.answers.region)) {
    state.errors.demographics = 'Please complete the required demographics fields.';
  }
  return Object.keys(state.errors).length === 0;
}

function nextStep() {
  if (!validateCurrentStep()) {
    render();
    return;
  }
  if (state.currentStep < steps.length - 1) {
    state.currentStep += 1;
    localStorage.setItem('gcsi-survey', JSON.stringify(state.answers));
    render();
  }
}

function prevStep() {
  if (state.currentStep > 0) {
    state.currentStep -= 1;
    render();
  }
}

function selectSector(value) {
  state.answers.sector = value;
  state.answers.organization = '';
  localStorage.setItem('gcsi-survey', JSON.stringify(state.answers));
  render();
}

function setAnswer(key, value) {
  state.answers[key] = value;
  localStorage.setItem('gcsi-survey', JSON.stringify(state.answers));
  render();
}

function toggleDimension(value, checked) {
  const current = state.answers.dimensions || [];
  state.answers.dimensions = checked ? [...current, value] : current.filter((item) => item !== value);
  localStorage.setItem('gcsi-survey', JSON.stringify(state.answers));
  render();
}

function toggleChannel(value, checked) {
  const current = state.answers.channels || [];
  state.answers.channels = checked ? [...current, value] : current.filter((item) => item !== value);
  localStorage.setItem('gcsi-survey', JSON.stringify(state.answers));
  render();
}

async function submitSurvey() {
  if (!validateCurrentStep()) {
    render();
    return;
  }

  state.isLoading = true;
  render();

  try {
    const response = await fetch('https://api.ghanacsi.org/response/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...state.answers,
        submittedAt: new Date().toISOString()
      })
    });

    const data = await response.json().catch(() => ({}));
    state.submissionMessage = data?.message || 'Your survey was submitted successfully.';
    state.submitted = true;
    localStorage.removeItem('gcsi-survey');
  } catch (error) {
    state.submissionMessage = 'We could not reach the endpoint. Please try again later.';
    state.submitted = true;
  } finally {
    state.isLoading = false;
    render();
  }
}

function resetSurvey() {
  state.currentStep = 0;
  state.answers = {};
  state.errors = {};
  state.isLoading = false;
  state.submitted = false;
  state.submissionMessage = '';
  localStorage.removeItem('gcsi-survey');
  render();
}

window.addEventListener('DOMContentLoaded', init);
window.nextStep = nextStep;
window.prevStep = prevStep;
window.selectSector = selectSector;
window.setAnswer = setAnswer;
window.toggleDimension = toggleDimension;
window.toggleChannel = toggleChannel;
window.submitSurvey = submitSurvey;
window.resetSurvey = resetSurvey;
