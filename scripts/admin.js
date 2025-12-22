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

  document.querySelectorAll('.tab').forEach(btn => {
  btn.onclick = () => {
    document.querySelectorAll('.tab').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.admin-block').forEach(b => b.classList.remove('active'));

    btn.classList.add('active');
    document.getElementById(btn.dataset.tab).classList.add('active');
  }
});

document.querySelectorAll("th[data-sort]").forEach(th => {
  th.onclick = () => {
    const index = th.cellIndex;
    const rows = [...th.closest("table").tbody.rows];

    rows.sort((a,b) =>
      a.cells[index].innerText.localeCompare(b.cells[index].innerText)
    );

    rows.forEach(r => th.closest("tbody").appendChild(r));
  };
});
