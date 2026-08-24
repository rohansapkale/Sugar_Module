// Sugar Desk Launcher for Frappe / ERPNext Desk (/app)
frappe.provide('sugar_module');

$(document).on('toolbar_setup', function() {
    sugar_module.add_sugar_desk_button();
});

$(document).ready(function() {
    sugar_module.add_sugar_desk_button();
});

sugar_module.add_sugar_desk_button = function() {
    if ($('#navbar-sugar-desk-btn').length) return;

    const btnHtml = `
        <li class="nav-item dropdown dropdown-notifications dropdown-mobile" id="navbar-sugar-desk-btn" style="margin-right: 8px;">
            <a class="nav-link btn btn-sm" href="/sugar-desk" style="background: #132b4e; color: #ffffff; font-weight: 600; font-size: 12px; padding: 5px 12px; border-radius: 6px; display: inline-flex; align-items: center; gap: 6px; text-decoration: none; border: 1px solid #2f6fd6; box-shadow: 0 1px 3px rgba(0,0,0,0.15);">
                <span>🌾</span>
                <span>Sugar Desk</span>
            </a>
        </li>
    `;

    // Try inserting before user profile dropdown or search bar
    if ($('.navbar .navbar-nav:last').length) {
        $('.navbar .navbar-nav:last').prepend(btnHtml);
    } else if ($('.navbar-collapse').length) {
        $('.navbar-collapse').append(btnHtml);
    }
};

// Global Keyboard Shortcut inside ERPNext: Alt+S -> Open Sugar Desk
$(document).on('keydown', function(e) {
    if (e.altKey && (e.key === 's' || e.key === 'S')) {
        if (!['input', 'textarea', 'select'].includes(document.activeElement.tagName.toLowerCase())) {
            e.preventDefault();
            window.location.href = '/sugar-desk';
        }
    }
});
