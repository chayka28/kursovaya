document.addEventListener("DOMContentLoaded", () => {
  // --------------------------
  // Toggle описание тезиса
  // --------------------------
  document.querySelectorAll('.toggle-description-btn').forEach(button => {
    button.addEventListener('click', (e) => {
      const thesisItem = e.target.closest('.thesis-item');
      const description = thesisItem.querySelector('.thesis-description');
      if (description.style.display === 'none' || description.style.display === '') {
        description.style.display = 'block';
      } else {
        description.style.display = 'none';
      }
    });
  });

  // --------------------------
  // Редактирование тезиса
  // --------------------------
  document.querySelectorAll('.edit-thesis-btn').forEach(button => {
    button.addEventListener('click', (e) => {
      const thesisId = button.getAttribute('data-id');
      const originalTitle = button.getAttribute('data-title');
      const originalAbstract = button.getAttribute('data-abstract');

      // Заполняем поля модалки
      document.getElementById('edit-title').value = originalTitle;
      document.getElementById('edit-abstract').value = originalAbstract;

      // Показываем модалку
      const modal = document.getElementById('edit-thesis-modal');
      modal.style.display = 'block';

      // Сохранение изменений
      document.getElementById('save-thesis-btn').onclick = async () => {
        const updatedTitle = document.getElementById('edit-title').value;
        const updatedAbstract = document.getElementById('edit-abstract').value;

        if (updatedTitle === originalTitle && updatedAbstract === originalAbstract) {
          alert('Вы не изменили данные');
          return;
        }

        try {
          const response = await fetch(`/thesis/edit/${thesisId}`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              title: updatedTitle,
              abstract: updatedAbstract,
            }),
          });

          const result = await response.json();

          if (response.ok) {
            location.reload(); // Обновляем страницу
          } else {
            alert(result.detail || 'Ошибка при редактировании тезиса');
          }
        } catch (err) {
          console.error(err);
          alert('Ошибка при редактировании тезиса');
        }
      };

      // Отмена редактирования
      document.getElementById('cancel-edit-btn').onclick = () => {
        modal.style.display = 'none';
      };
    });
  });

  // --------------------------
  // Удаление тезиса
  // --------------------------
  document.querySelectorAll('.button.delete-thesis-btn').forEach(button => {
    button.addEventListener('click', (e) => {
      const thesisId = button.getAttribute('data-id');
      const modal = document.getElementById('confirm-delete-modal');
      modal.style.display = 'block';

      document.getElementById('confirm-delete').onclick = async () => {
        try {
          const response = await fetch(`/thesis/delete/${thesisId}`, {
            method: 'POST',
          });

          const result = await response.json();

          if (response.ok) {
            // Удаляем тезис из DOM
            const thesisElement = document.getElementById(`thesis-${thesisId}`);
            if (thesisElement) thesisElement.remove();
            modal.style.display = 'none';
          } else {
            alert(result.detail || 'Ошибка при удалении тезиса');
          }
        } catch (err) {
          console.error(err);
          alert('Ошибка при удалении тезиса');
        }
      };

      document.getElementById('cancel-delete').onclick = () => {
        modal.style.display = 'none';
      };
    });
  });

  // --------------------------
  // Закрытие модалок при клике вне области
  // --------------------------
  window.addEventListener('click', (e) => {
    const editModal = document.getElementById('edit-thesis-modal');
    const deleteModal = document.getElementById('confirm-delete-modal');
    if (e.target === editModal) editModal.style.display = 'none';
    if (e.target === deleteModal) deleteModal.style.display = 'none';
  });
});
