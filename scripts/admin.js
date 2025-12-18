  // Обработчик для подтверждения заявки
  document.querySelectorAll('.approve-btn').forEach(button => {
    button.addEventListener('click', async (e) => {
      const appId = e.target.getAttribute('data-id');
      
      try {
        const response = await fetch(`/admin/application/${appId}/approve`, {
          method: 'POST',
        });
        const result = await response.json();
        
        if (response.ok) {
          // Обновляем статус заявки на "approved"
          const row = document.getElementById(`application-${appId}`);
          row.querySelector('.status').textContent = "approved";
          row.querySelector('.status').classList.add('approved');
        } else {
          alert(result.detail || 'Ошибка при подтверждении заявки');
        }
      } catch (error) {
        console.error('Ошибка при отправке запроса:', error);
      }
    });
  });

  // Обработчик для отклонения заявки
  document.querySelectorAll('.reject-btn').forEach(button => {
    button.addEventListener('click', async (e) => {
      const appId = e.target.getAttribute('data-id');
      
      try {
        const response = await fetch(`/admin/application/${appId}/reject`, {
          method: 'POST',
        });
        const result = await response.json();
        
        if (response.ok) {
          // Обновляем статус заявки на "rejected"
          const row = document.getElementById(`application-${appId}`);
          row.querySelector('.status').textContent = "rejected";
          row.querySelector('.status').classList.add('rejected');
        } else {
          alert(result.detail || 'Ошибка при отклонении заявки');
        }
      } catch (error) {
        console.error('Ошибка при отправке запроса:', error);
      }
    });
  });