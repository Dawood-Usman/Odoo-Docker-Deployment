{
    'name': 'Prixite Website Theme',
    'version': '1.0',
    'summary': 'Prixite Website Theme',
    'sequence': 10,
    'description': 'Prixite Website Theme',
    'category': 'Theme/Creative',
    'website': 'prixite.com',
    'license': 'LGPL-3',
    'depends': ['base', 'website', 'web', 'contacts', 'website_blog'],
    'data': [
        'security/ir.model.access.csv',
        'views/sections/head_section.xml',
        'views/sections/header_section.xml',
        'views/sections/footer_section.xml',

        'views/services/web_development.xml',
        'views/services/machine-learning.xml',
        'views/services/devops.xml',
        'views/services/scraping.xml',
        'views/services/python-programming.xml',
        'views/services/mobile-app-development.xml',
        'views/services/odoo.xml',
        'views/services/react-development.xml',

        'views/services_page.xml',
        'views/home_page.xml',
        'views/about_page.xml',
        'views/blog_page.xml',

        'views/contact_page.xml',
        'views/thankyou.xml',
        'views/contact/contact_view.xml',

        # 'views/blogs/blog_post_view.xml',
        # 'views/blogs/blog_detail.xml',
        # 'views/blogs/blog_defualt_list.xml',
        'views/blogs/blog_detail_templates.xml',

        'views/team_page.xml',
        'views/teams/team_member.xml',
        'views/teams/team_detail.xml',

        'views/testimonials/testimonials_view.xml'
    ],
    'assets': {
        'web._assets_primary_variables': [
            ('prepend', 'prixite_theme/static/scss/primary_variables.scss'),
        ],

        'web.assets_frontend': [
            '/prixite_theme/static/scss/home.scss',
            '/prixite_theme/static/scss/about-us.scss',
            '/prixite_theme/static/scss/contact-us.scss',
            '/prixite_theme/static/scss/service.scss',
            '/prixite_theme/static/scss/header.scss',
        ]
    },
}
