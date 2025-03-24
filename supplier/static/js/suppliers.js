function showModal() {
    const modal = document.getElementById('delete-modal');
    modal.classList.add('show');
}

function closeModal() {
    const modal = document.getElementById('delete-modal');
    modal.classList.remove('show');
}

function confirmDelete(button) {
    const id = button.getAttribute('data-id');
    const name = button.getAttribute('data-name');

    document.getElementById('supplier-name').textContent = name;
    document.getElementById('delete-form').action = `/delete-supplier/${id}/`;

    showModal();
}

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('supplier-search');

    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            const query = this.value.trim();
            searchSuppliers(query);
        }, 500));
    }

    function searchSuppliers(query) {
        fetch(`/search-supplier/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                updateSupplierTable(data.suppliers);
            })
            .catch(error => {
                console.error('Error searching suppliers:', error);
            });
    }

    function updateSupplierTable(suppliers) {
        const tableBody = document.querySelector('.data-table tbody');

        if (!tableBody) return;

        tableBody.innerHTML = '';

        if (suppliers.length === 0) {
            const row = document.createElement('tr');
            row.innerHTML = '<td colspan="8" class="text-center">No suppliers found</td>';
            tableBody.appendChild(row);
            return;
        }

        suppliers.forEach(supplier => {
            const row = document.createElement('tr');
            row.innerHTML = `
        <td>${supplier.id}</td>
        <td>${supplier.name}</td>
        <td>${supplier.contact}</td>
        <td>${supplier.phone}</td>
        <td>${supplier.email}</td>
        <td class="address-cell">${supplier.address}</td>
        <td>${supplier.created}</td>
        <td class="actions-cell">
          <div class="action-buttons">
            <a href="/view-supplier/${supplier.id}/" class="btn-icon btn-view" title="View">
              <i class="fas fa-eye"></i>
            </a>
            <a href="/edit-supplier/${supplier.id}/" class="btn-icon btn-edit" title="Edit">
              <i class="fas fa-edit"></i>
            </a>
            <button class="btn-icon btn-delete" title="Delete"
                    data-id="${supplier.id}"
                    data-name="${supplier.name}"
                    onclick="confirmDelete(this)">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </td>
      `;
            tableBody.appendChild(row);
        });
    }

    function debounce(func, wait) {
        let timeout;
        return function() {
            const context = this, args = arguments;
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                func.apply(context, args);
            }, wait);
        };
    }
});