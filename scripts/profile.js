document.addEventListener("DOMContentLoaded", () => {
  // Открытие и закрытие описания тезиса
  document.querySelectorAll('.toggle-description-btn').forEach(button => {
    button.addEventListener('click', (e) => {
      const thesisItem = e.target.closest('.thesis-item');
      thesisItem.classList.toggle('open'); // Переключаем класс, чтобы анимация сработала
    });
  });

  // Открытие модального окна для редактирования
  document.querySelectorAll('.edit-thesis-btn').forEach(button => {
    button.addEventListener('click', (e) => {
      const thesisId = e.target.getAttribute('data-id');
      const title = e.target.getAttribute('data-title');
      const abstract = e.target.getAttribute('data-abstract');
      
      document.getElementById('edit-title').value = title;
      document.getElementById('edit-abstract').value = abstract;
      
      const modal = document.getElementById('edit-thesis-modal');
      modal.style.display = 'block';

      // Обработчик для сохранения изменений
      document.getElementById('save-thesis-btn').onclick = async () => {
        const updatedTitle = document.getElementById('edit-title').value;
        const updatedAbstract = document.getElementById('edit-abstract').value;

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
          location.reload();  // Обновляем страницу, чтобы отобразить изменения
        } else {
          alert(result.detail || 'Ошибка при редактировании тезиса');
        }
      };

      // Закрытие модального окна
      document.getElementById('cancel-edit-btn').onclick = () => {
        modal.style.display = 'none';
      };
    });
  });

  // Удаление тезиса
  document.querySelectorAll('.delete-thesis-btn').forEach(button => {
    button.addEventListener('click', async (e) => {
      const thesisId = e.target.getAttribute('data-id');

      const response = await fetch(`/thesis/delete/${thesisId}`, {
        method: 'POST'
      });

      const result = await response.json();
      if (response.ok) {
        document.getElementById(`thesis-${thesisId}`).remove();  // Удаляем тезис из DOM
      } else {
        alert(result.detail || 'Ошибка при удалении тезиса');
      }
    });
  });
});
