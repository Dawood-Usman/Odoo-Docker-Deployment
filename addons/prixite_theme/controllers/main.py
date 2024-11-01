import json
import pdb

from odoo import http
from odoo.http import request
from bs4 import BeautifulSoup


class IndexController(http.Controller):
    @http.route('/', auth='public', website=True)
    def index(self):
        testimonials = http.request.env['testimonials'].sudo().search([])
        BlogPost = http.request.env['blog.post']
        posts = []
        for post in BlogPost.search([], limit=2):
            soup = BeautifulSoup(post.content, 'html.parser')
            image = soup.find('img')
            posts.append((post, image and image.get('src', '..') or False))
        return http.request.render('prixite_theme.prixite_homepage', {
            'testimonials': testimonials,
            'posts': posts,
        })


class BlogController(http.Controller):
    @http.route('/blogss', auth='public', website=True)
    def blogs(self, **kw):
        blogs = request.env['blog.post'].sudo().search([])
        return http.request.render('prixite_theme.template_blogs_listing', {'blogs': blogs, })


#
#     @http.route(['/blogs/<slug>'], auth='public', website=True)
#     def blog_detail_slug(self, slug, **kw):
#         post = http.request.env['blog.post'].search([('slug', '=', slug)], limit=1)
#         if not post:
#             return http.request.not_found()
#         formatted_date = post.create_date.strftime("%B %d, %Y")
#         return http.request.render('prixite_theme.template_blog_detail', {
#             'post': post,
#             'formatted_date': formatted_date
#         })


class TeamController(http.Controller):
    @http.route('/team', auth='public', website=True)
    def teams(self):
        TeamCategory = http.request.env['team.category'].sudo()
        TeamMember = http.request.env['team.member'].sudo()
        categories = TeamCategory.search([])
        teams = TeamMember.search([])

        # Construct base URL
        base_url = http.request.env['ir.config_parameter'].sudo().get_param('web.base.url')

        categories_data = [{
            'id': category.id,
            'name': category.name,
        } for category in categories]

        teams_data = [{
            'id': team.id,
            'name': team.name,
            'title': team.title,
            'image': f"{base_url}/web/image?model=team.member&id={team.id}&field=profile",
            'category_ids': team.category_ids.ids,
        } for team in teams]

        return http.request.render('prixite_theme.template_team_listing', {
            'categories_json': json.dumps(categories_data),
            'teams_json': json.dumps(teams_data),
        })

    @http.route(['/teams/<model("team.member"):team>'], auth='public', website=True)
    def teams_detail(self, team, **kw):
        base_url = http.request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        # team.image = f"{base_url}/web/image?model=team.member&id={team.id}&field=profile"
        return http.request.render('prixite_theme.template_team_details', {'team': team})


class ContactFormController(http.Controller):
    @http.route('/contact/submit', type='http', auth="public", methods=['POST'], website=True)
    def submit(self, **kw):
        request.env['contact'].sudo().create({
            'name': kw.get('name'),
            'email': kw.get('email'),
            'phone': kw.get('phone'),
            'company': kw.get('company'),
            'message': kw.get('message'),
        })
        return request.redirect('/thank-you')


class WebsiteMenuController(http.Controller):

    @http.route('/api/menu', auth='public', type='http')
    def header_menu_items(self):
        static_data = [
            # {'name': 'About Us', 'url': '/about-us'},
            # {'name': 'Services', 'url': '/services'},
            # {'name': 'Contact Us', 'url': '/contact'},
            # {'name': 'Meet the Team', 'url': '/team'},
            # {'name': 'News & Blogs', 'url': '/blogs'},
        ]

        top_menu_children_data = []
        menus = request.env['website.menu'].sudo().search([('parent_id', '=', False)])
        for menu in menus:
            if menu.name == 'Top Menu for Website 1':
                top_menu_children_data = [{'name': child.name, 'url': child.url} for child in menu.child_id]
                break

        for item in reversed(static_data):
            top_menu_children_data.insert(0, item)

        return json.dumps(top_menu_children_data)
