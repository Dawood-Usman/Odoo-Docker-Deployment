<script>
        $(document).ready(function () {
        alert("alert");
            // Parse the category data from the hidden p element
            var categories = JSON.parse($('#category').text());

            // Loop through each category to create tabs and tab content
            categories.forEach(function (category, index) {
                // Create a new list item for the tab
                var tabClass = index === 0 ? 'nav-item active' : 'nav-item';
                var tabLinkClass = index === 0 ? 'nav-link active' : 'nav-link';
                var tabItem = $('<li>', {class: tabClass, role: 'presentation'})
                    .append($('<a>', {
                        class: tabLinkClass,
                        id: 'tab-' + category.id,
                        'data-toggle': 'tab',
                        href: '#panel-' + category.id,
                        role: 'tab',
                        text: category.name
                    }));

                // Append the new tab to the tabs list
                $('#myTab').append(tabItem);

                // Create the tab content
                var paneClass = index === 0 ? 'tab-pane fade show active' : 'tab-pane fade';
                var tabContent = $('<div>', {
                    class: paneClass,
                    id: 'panel-' + category.id,
                    role: 'tabpanel',
                    'aria-labelledby': 'tab-' + category.id
                }).html('<h4>' + category.name + '</h4><p>' + category.description + '</p>');

                // Append the new content to the tab content container
                $('#tab-content').append(tabContent);
            });
        });
    </script>