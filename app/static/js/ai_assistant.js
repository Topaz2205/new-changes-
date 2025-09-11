document.addEventListener('DOMContentLoaded', () => {
    const form   = document.getElementById('ask-form');
    const textarea = document.getElementById('query');
    const btn    = document.getElementById('ask-btn');
    const status = document.getElementById('status');
    const card   = document.getElementById('answer-card');
    const answer = document.getElementById('answer');
    const sources= document.getElementById('sources');
  
    async function askServer(q) {
      const res = await fetch('/ai/ask', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ query: q })
      });
      if (!res.ok) {
        const t = await res.text().catch(()=>'');
        throw new Error(`שגיאה בשרת (${res.status}): ${t || res.statusText}`);
      }
      return res.json();
    }
  
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const q = textarea.value.trim();
      if (!q) return;
  
      btn.disabled = true;
      status.textContent = 'חושב...';
      answer.textContent = '';
      sources.innerHTML = '';
      card.classList.add('hidden');
  
      try {
        const data = await askServer(q);
        answer.textContent = (data.answer || '').trim();
        // הצגת מקורות יפה
        if (Array.isArray(data.sources) && data.sources.length) {
          const title = document.createElement('div');
          title.className = 'sources-title';
          title.textContent = 'מקורות:';
          sources.appendChild(title);
  
          const list = document.createElement('div');
          list.className = 'source-list';
          data.sources.forEach(s => {
            const chip = document.createElement('span');
            chip.className = 'source-chip';
            chip.textContent = `${s.kind || 'item'} #${s.id ?? '?'}`;
            list.appendChild(chip);
          });
          sources.appendChild(list);
        }
        card.classList.remove('hidden');
        status.textContent = '';
      } catch (err) {
        status.textContent = err.message || 'שגיאה';
      } finally {
        btn.disabled = false;
      }
    });
  });
  