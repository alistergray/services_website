async function loadPosts() {
  try {
    const response = await fetch('data/posts.json');
    const posts = await response.json();
    const list = document.getElementById('posts-list');
    const container = document.getElementById('posts');
    if (list) {
      list.innerHTML = posts.map(p => `<li><strong>${p.title}</strong> (${p.created_at})</li>`).join('');
    }
    if (container) {
      container.innerHTML = posts.map(p => `
        <article>
          <h2>${p.title}</h2>
          <p>${p.content}</p>
          <small>${p.created_at}</small>
        </article>`).join('');
    }
  } catch (err) {
    console.error('Error loading posts', err);
  }
}

window.addEventListener('DOMContentLoaded', loadPosts);
