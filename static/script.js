const fileInput = document.getElementById('fileInput');
const fileNames = document.getElementById('fileNames');
const result = document.getElementById('result');
const uploadButton = document.getElementById('uploadButton');
const cardContainer = document.getElementById('cardContainer');

fileInput.addEventListener('change', function() {
    result.textContent = '';

    if (this.files.length === 0) {
        fileNames.textContent = 'Файлы не выбраны'; 
    } else if (this.files.length === 1) {
        fileNames.textContent = `Выбран файл: ${this.files[0].name}`;
    } else {
        fileNames.textContent = `Выбрано файлов: ${this.files.length}`;
    }
});

async function fileUploading() {
    const files = fileInput.files;
    
    if (files.length === 0) {
        result.innerHTML = `<div class="error">Пожалуйста, выберите файлы</div>`;
        return;
    }
    
    uploadButton.disabled = true;
    result.textContent = 'Загрузка...';
    cardContainer.innerHTML = '';

    const reportButton = document.getElementById('reportButton');
    reportButton.classList.remove('visible');
    
    try {
        const formData = new FormData();
        
        for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i])
        }
        
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const responseData = await response.json();
        if (response.ok) {
            if (responseData.all_valid) {
                result.innerHTML = `<div class="success">Все файлы успешно загружены</div>`;
            } else {
                let invalidData = responseData.invalid ? responseData.invalid.join(', ') : 'нет';
                result.innerHTML = `<div class="error">Необработанные файлы: ${invalidData}</div>`;
            }

            showCards(responseData);
        }
    } catch (error) {
        result.innerHTML = `<div class="error">Ошибка сети: ${error.message}</div>`;
        console.error('Ошибка:', error);
    } finally {
        uploadButton.disabled = false;
    }
}

function downloadReport() {
    window.location.href = '/download-report';
}

function showCards(data) {
    let cardsHTML = '';
    let is_any_card = false;

    if (data.valid && data.valid.length > 0) {
        data.valid.forEach(imageName => {
            cardsHTML += `
                <div class="card-valid">
                    <div class="card-header-valid">
                        <div class="image-name-valid" title="${imageName}">${imageName}</div>
                        <div class="verdict-valid">Подходит</div>
                    </div>
                </div>
            `;
        });
        is_any_card = true;
    }

    if (data.unsuitable && data.unsuitable.length > 0) {
        data.unsuitable.forEach(item => {
            const imageName = Object.keys(item)[0];
            const errors = item[imageName];
            cardsHTML += `
                <div class="card-invalid">
                    <div class="card-header-invalid">
                        <div class="image-name-invalid" title="${imageName}">${imageName}</div>
                        <div class="verdict-invalid">Не подходит</div>
                    </div>
                    <div>
                        ${errors.map(error => `
                            <div class="error-item">${error}</div>
                        `).join('')}
                    </div>
                </div>
            `;
        });
        is_any_card = true

        const reportButton = document.getElementById('reportButton');
        if (is_any_card) {
            reportButton.classList.add('visible');
        } else {
            reportButton.classList.remove('visible');
        }
    }


    cardContainer.innerHTML = cardsHTML;
}

function applyCardSymmetry() {
    const cards = cardContainer.querySelectorAll('.card');
    const totalCards = cards.length;
    
    if (totalCards === 0) return;
    
    const cardsPerRow = window.innerWidth > 1200 ? 3 : (window.innerWidth > 768 ? 2 : 1);
    const cardsInLastRow = totalCards % cardsPerRow;
    

    cards.forEach(card => {
        card.style.gridColumn = '';
        card.style.justifySelf = '';
        card.style.maxWidth = '';
    });
    
    if (cardsInLastRow > 0 && cardsInLastRow < cardsPerRow) {
        if (cardsInLastRow === 1) {
            const lastCard = cards[totalCards - 1];
            if (cardsPerRow === 3) {
                lastCard.style.gridColumn = '2';
            } else if (cardsPerRow === 2) {
                lastCard.style.gridColumn = '1 / -1';
                lastCard.style.justifySelf = 'center';
                lastCard.style.maxWidth = '50%';
            }
        } else if (cardsInLastRow === 2 && cardsPerRow === 3) {
            const secondLastCard = cards[totalCards - 2];
            const lastCard = cards[totalCards - 1];
            secondLastCard.style.gridColumn = '1';
            lastCard.style.gridColumn = '2';
        }
    }
}

window.addEventListener('resize', applyCardSymmetry);