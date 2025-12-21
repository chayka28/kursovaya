document.addEventListener("DOMContentLoaded", () => {

  // ===== Toggle тезиса =====
  document.querySelectorAll('.toggle-description-btn').forEach(button => {
    button.addEventListener('click', () => {
      const thesisItem = button.closest('.thesis-item');
      thesisItem.classList.toggle('open');
    });
  });

  // ===== Редактирование =====
  document.querySelectorAll('.edit-thesis-btn').forEach(button => {
    button.addEventListener('click', () => {
      const thesisId = button.dataset.id;

      document.getElementById('edit-title').value = button.dataset.title;
      document.getElementById('edit-abstract').value = button.dataset.abstract;

      const modal = document.getElementById('edit-thesis-modal');
      modal.style.display = 'flex';

      document.getElementById('save-thesis-btn').onclick = async () => {
        const title = document.getElementById('edit-title').value;
        const abstract = document.getElementById('edit-abstract').value;

        const response = await fetch(`/thesis/edit/${thesisId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title, abstract })
        });

        if (response.ok) {
          location.reload();
        } else {
          alert('Ошибка сохранения');
        }
      };

      document.getElementById('cancel-edit-btn').onclick = () => {
        modal.style.display = 'none';
      };
    });
  });

  // ===== Удаление =====
  document.querySelectorAll('.delete-thesis-btn').forEach(button => {
    button.addEventListener('click', () => {
      const thesisId = button.dataset.id;
      const modal = document.getElementById('confirm-delete-modal');
      modal.style.display = 'flex';

      document.getElementById('confirm-delete').onclick = async () => {
        const response = await fetch(`/thesis/delete/${thesisId}`, { method: 'POST' });

        if (response.ok) {
          document.getElementById(`thesis-${thesisId}`)?.remove();
          modal.style.display = 'none';
        } else {
          alert('Ошибка удаления');
        }
      };

      document.getElementById('cancel-delete').onclick = () => {
        modal.style.display = 'none';
      };
    });
  });

  // ===== Клик вне модалки =====
  window.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
      e.target.style.display = 'none';
    }
  });

});
