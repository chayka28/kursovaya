document.addEventListener("DOMContentLoaded", () => {
  // Открытие и закрытие описания тезиса
  document.querySelectorAll('.toggle-description-btn').forEach(button => {
    button.addEventListener('click', (e) => {
      const thesisItem = e.target.closest('.thesis-item');
      thesisItem.classList.toggle('open');
    });
  });

  // Открытие модального окна для редактирования
  document.querySelectorAll('.edit-thesis-btn').forEach(button => {
    button.addEventListener('click', (e) => {
      const thesisId = e.target.getAttribute('data-id');
      const originalTitle = e.target.getAttribute('data-title');
      const originalAbstract = e.target.getAttribute('data-abstract');
      
      document.getElementById('edit-title').value = originalTitle;
      document.getElementById('edit-abstract').value = originalAbstract;
      
      const modal = document.getElementById('edit-thesis-modal');
      modal.style.display = 'block';

      document.getElementById('save-thesis-btn').onclick = async () => {
        const updatedTitle = document.getElementById('edit-title').value;
        const updatedAbstract = document.getElementById('edit-abstract').value;

        // Если данные не изменились
        if (updatedTitle === originalTitle && updatedAbstract === originalAbstract) {
          alert('Вы не изменили данные');
          return;
        }

        const response = await fetch(`/thesis/edit/${thesisId}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            title: updatedTitle,
            abstract: updatedAbstract,
          })
        });

        const result = await response.json();
        if (response.ok) {
          location.reload();  // Обновляем страницу
        } else {
          alert(result.detail || 'Ошибка при редактировании тезиса');
        }
      };

      document.getElementById('cancel-edit-btn').onclick = () => {
        modal.style.display = 'none';
      };
    });
  });

  // Удаление тезиса
  document.querySelectorAll('.delete-thesis-btn').forEach(button => {
    button.addEventListener('click', (e) => {
      const thesisId = e.target.getAttribute('data-id');
      
      const modal = document.getElementById('confirm-delete-modal');
      modal.style.display = 'block';

      document.getElementById('confirm-delete').onclick = async () => {
        const response = await fetch(`/thesis/delete/${thesisId}`, {
          method: 'POST'
        });

        const result = await response.json();
        if (response.ok) {
          document.getElementById(`thesis-${thesisId}`).remove();  // Удаляем тезис из DOM
          modal.style.display = 'none';  // Закрываем модалку
        } else {
          alert(result.detail || 'Ошибка при удалении тезиса');
        }
      };

      document.getElementById('cancel-delete').onclick = () => {
        modal.style.display = 'none';
      };
    });
  });
});
