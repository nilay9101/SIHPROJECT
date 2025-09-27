class MindWellAssessment {
    constructor() {
        this.currentAssessment = null;
        this.currentQuestionIndex = 0;
        this.responses = [];
        this.authToken = localStorage.getItem('access_token');
    }

    async startAssessment(assessmentType) {
        try {
            const response = await fetch(`http://localhost:8000/api/assessment/questions/${assessmentType}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.authToken}`
                }
            });

            if (!response.ok) {
                if (response.status === 401) {
                    alert('Please log in to take assessments');
                    window.location.href = '/login.html';
                    return;
                }
                throw new Error('Failed to load assessment questions');
            }

            const data = await response.json();
            this.currentAssessment = data;
            this.currentQuestionIndex = 0;
            this.responses = new Array(data.questions.length).fill(null);
            
            this.showAssessmentModal();
            this.displayCurrentQuestion();
            
        } catch (error) {
            console.error('Error starting assessment:', error);
            alert('Error loading assessment. Please try again.');
        }
    }

    showAssessmentModal() {
        // Check if modal already exists
        let existingModal = document.getElementById('assessmentModal');
        
        if (!existingModal) {
            // Create modal HTML only if it doesn't exist
            const modalHTML = `
                <div class="modal fade" id="assessmentModal" tabindex="-1" aria-labelledby="assessmentModalLabel" aria-hidden="true">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="assessmentModalLabel">${this.currentAssessment.assessment_type} Assessment</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <div class="assessment-progress mb-4">
                                    <div class="progress">
                                        <div class="progress-bar" role="progressbar" style="width: 0%"></div>
                                    </div>
                                    <small class="text-muted">Question <span id="currentQuestionNum">1</span> of ${this.currentAssessment.questions.length}</small>
                                </div>
                                
                                <div class="assessment-instructions mb-4">
                                    <p class="text-muted">${this.currentAssessment.instructions}</p>
                                </div>
                                
                                <div id="assessmentQuestion" class="mb-4">
                                    <!-- Question will be loaded here -->
                                </div>
                                
                                <div id="assessmentScale" class="mb-4">
                                    <!-- Scale options will be loaded here -->
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" id="prevQuestionBtn" onclick="assessment.previousQuestion()" disabled>Previous</button>
                                <button type="button" class="btn btn-primary" id="nextQuestionBtn" onclick="assessment.nextQuestion()">Next</button>
                                <button type="button" class="btn btn-success" id="submitAssessmentBtn" onclick="assessment.submitAssessment()" style="display: none;">Submit Assessment</button>
                            </div>
                        </div>
                    </div>
                </div>
                <style>
                     #assessmentQuestion, #assessmentScale {
                         transition: opacity 0.2s ease-in-out;
                     }
                     
                     .question-card {
                         background: #f8f9fa;
                         border-radius: 10px;
                         padding: 1.5rem;
                         margin-bottom: 1rem;
                         border-left: 4px solid #6a5acd;
                         box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                     }
                     
                     .question-card h5 {
                         color: #6a5acd;
                         font-weight: 600;
                         margin-bottom: 1rem;
                     }
                     
                     .question-card .lead {
                         font-size: 1.1rem;
                         line-height: 1.6;
                         margin-bottom: 0;
                     }
                     
                     #assessmentScale .form-check {
                         background: white;
                         padding: 0.75rem;
                         border-radius: 8px;
                         margin-bottom: 0.5rem;
                         border: 1px solid #e9ecef;
                         transition: all 0.2s ease;
                     }
                     
                     #assessmentScale .form-check:hover {
                         background: #f8f9fa;
                         border-color: #6a5acd;
                         transform: translateY(-1px);
                     }
                     
                     #assessmentScale .form-check-input:checked + .form-check-label {
                         font-weight: 600;
                         color: #6a5acd;
                     }
                     
                     .assessment-progress .progress {
                         height: 8px;
                         border-radius: 10px;
                         background-color: #e9ecef;
                     }
                     
                     .assessment-progress .progress-bar {
                         background: linear-gradient(135deg, #6a5acd, #9370db);
                         border-radius: 10px;
                         transition: width 0.3s ease;
                     }
                 </style>
            `;
            
            document.body.insertAdjacentHTML('beforeend', modalHTML);
            
            // Handle modal close only once when creating
            document.getElementById('assessmentModal').addEventListener('hidden.bs.modal', function () {
                this.currentAssessment = null;
                this.currentQuestionIndex = 0;
                this.responses = [];
            }.bind(this));
        } else {
            // Update existing modal title
            document.getElementById('assessmentModalLabel').textContent = `${this.currentAssessment.assessment_type} Assessment`;
            // Update progress info
            document.querySelector('.assessment-instructions p').textContent = this.currentAssessment.instructions;
            document.querySelector('.text-muted small').innerHTML = `Question <span id="currentQuestionNum">1</span> of ${this.currentAssessment.questions.length}`;
        }
        
        // Show the modal
        const modal = new bootstrap.Modal(document.getElementById('assessmentModal'));
        modal.show();
    }

    displayCurrentQuestion() {
        const question = this.currentAssessment.questions[this.currentQuestionIndex];
        const questionNum = this.currentQuestionIndex + 1;
        
        // Get containers
        const questionContainer = document.getElementById('assessmentQuestion');
        const scaleContainer = document.getElementById('assessmentScale');
        
        // Ensure containers exist
        if (!questionContainer || !scaleContainer) {
            console.error('Assessment containers not found');
            return;
        }
        
        // Add fade effect for smooth transition
        questionContainer.style.opacity = '0.5';
        scaleContainer.style.opacity = '0.5';
        
        // Small delay to show transition
        setTimeout(() => {
            // Clear previous content completely
            questionContainer.innerHTML = '';
            scaleContainer.innerHTML = '';
            
            // Update question number
            const questionNumElement = document.getElementById('currentQuestionNum');
            if (questionNumElement) {
                questionNumElement.textContent = questionNum;
            }
            
            // Create new question content
            const questionHTML = `
                <div class="question-card">
                    <h5>Question ${questionNum}</h5>
                    <p class="lead">${question.text}</p>
                </div>
            `;
            questionContainer.innerHTML = questionHTML;

            // Create scale options with proper radio button management
            const scaleHTML = this.currentAssessment.scale.map(option => `
                <div class="form-check mb-3">
                    <input class="form-check-input" type="radio" name="assessmentResponse" 
                           id="response${option.value}" value="${option.value}" 
                           ${this.responses[this.currentQuestionIndex] === option.value ? 'checked' : ''}>
                    <label class="form-check-label" for="response${option.value}">
                        ${option.label}
                    </label>
                </div>
            `).join('');
            
            scaleContainer.innerHTML = scaleHTML;

            // Fade back in
            questionContainer.style.opacity = '1';
            scaleContainer.style.opacity = '1';

            // Update progress bar
            const progress = ((this.currentQuestionIndex + 1) / this.currentAssessment.questions.length) * 100;
            const progressBar = document.querySelector('.progress-bar');
            if (progressBar) {
                progressBar.style.width = `${progress}%`;
            }

            // Update button states
            const prevBtn = document.getElementById('prevQuestionBtn');
            const nextBtn = document.getElementById('nextQuestionBtn');
            const submitBtn = document.getElementById('submitAssessmentBtn');
            
            if (prevBtn) prevBtn.disabled = this.currentQuestionIndex === 0;
            
            if (this.currentQuestionIndex === this.currentAssessment.questions.length - 1) {
                if (nextBtn) nextBtn.style.display = 'none';
                if (submitBtn) submitBtn.style.display = 'block';
            } else {
                if (nextBtn) nextBtn.style.display = 'block';
                if (submitBtn) submitBtn.style.display = 'none';
            }
        }, 150);
    }

    nextQuestion() {
        const selectedResponse = document.querySelector('input[name="assessmentResponse"]:checked');
        if (!selectedResponse) {
            alert('Please select a response before continuing.');
            return;
        }

        this.responses[this.currentQuestionIndex] = parseInt(selectedResponse.value);
        
        if (this.currentQuestionIndex < this.currentAssessment.questions.length - 1) {
            this.currentQuestionIndex++;
            this.displayCurrentQuestion();
        }
    }

    previousQuestion() {
        if (this.currentQuestionIndex > 0) {
            this.currentQuestionIndex--;
            this.displayCurrentQuestion();
        }
    }

    async submitAssessment() {
        const selectedResponse = document.querySelector('input[name="assessmentResponse"]:checked');
        if (!selectedResponse) {
            alert('Please select a response before submitting.');
            return;
        }

        this.responses[this.currentQuestionIndex] = parseInt(selectedResponse.value);

        // Check if all questions are answered
        if (this.responses.some(response => response === null)) {
            alert('Please answer all questions before submitting.');
            return;
        }

        try {
            const assessmentData = {
                assessment_type: this.currentAssessment.assessment_type,
                responses: this.responses.map((score, index) => ({
                    question_id: index,
                    score: score
                }))
            };

            const response = await fetch('http://localhost:8000/api/assessment/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.authToken}`
                },
                body: JSON.stringify(assessmentData)
            });

            if (!response.ok) {
                throw new Error('Failed to submit assessment');
            }

            const result = await response.json();
            this.displayResults(result);
            
        } catch (error) {
            console.error('Error submitting assessment:', error);
            alert('Error submitting assessment. Please try again.');
        }
    }

    displayResults(result) {
        const modalBody = document.querySelector('#assessmentModal .modal-body');
        
        let severityColor = 'success';
        if (result.severity_level === 'moderate') severityColor = 'warning';
        if (result.severity_level === 'moderately_severe' || result.severity_level === 'severe') severityColor = 'danger';

        modalBody.innerHTML = `
            <div class="assessment-results">
                <h4 class="text-center mb-4">Assessment Results</h4>
                
                <div class="alert alert-${severityColor} text-center">
                    <h5>Your ${result.assessment_type} Score: ${result.total_score}</h5>
                    <p class="mb-0">Severity Level: <strong>${result.severity_level.replace('_', ' ').toUpperCase()}</strong></p>
                </div>

                <div class="recommendations mt-4">
                    <h6>Recommendations:</h6>
                    <ul class="list-group">
                        ${result.recommendations.map(rec => rec ? `<li class="list-group-item">${rec}</li>` : '').join('')}
                    </ul>
                </div>

                <div class="text-center mt-4">
                    <button class="btn btn-primary me-2" onclick="assessment.downloadResults()">Download Results</button>
                    <button class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        `;

        // Update footer
        document.querySelector('#assessmentModal .modal-footer').innerHTML = `
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
        `;
    }

    downloadResults() {
        const results = {
            assessment_type: this.currentAssessment.assessment_type,
            responses: this.responses,
            timestamp: new Date().toISOString(),
            user: JSON.parse(localStorage.getItem('user') || '{}')
        };

        const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `mindwell-assessment-${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    async loadAssessmentHistory() {
        try {
            const response = await fetch('http://localhost:8000/api/assessment/history', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.authToken}`
                }
            });

            if (!response.ok) {
                if (response.status === 401) {
                    return null; // Not logged in
                }
                throw new Error('Failed to load assessment history');
            }

            return await response.json();
        } catch (error) {
            console.error('Error loading assessment history:', error);
            return null;
        }
    }
}

// Initialize assessment system - make it global
window.assessment = new MindWellAssessment();

// Add event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add click handlers to assessment buttons
    const assessmentButtons = document.querySelectorAll('#assessment .btn-primary');
    assessmentButtons.forEach((button, index) => {
        button.addEventListener('click', function() {
            const assessmentType = index === 0 ? 'PHQ-9' : 'GAD-7';
            assessment.startAssessment(assessmentType);
        });
    });
});