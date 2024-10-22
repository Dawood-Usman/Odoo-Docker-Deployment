import html2text
import re
from odoo import models, fields, api

# class BlogPost(models.Model):
#     _name = 'blog.post'
#     _description = 'Blog Post'
#
#     title = fields.Char(string='Title', required=True)
#     description = fields.Html(string='Description', sanitize=True, strip_style=False)
#     image = fields.Binary(string='Image')
#     created_at = fields.Datetime(string='Created At', default=fields.Datetime.now)
#     read_time = fields.Char(string='Read Time', compute='_compute_read_time', store=True)
#     user_id = fields.Many2one('res.users', string='User', required=True, ondelete='cascade',
#                               default=lambda self: self.env.user)
#     slug = fields.Char(string='Slug', compute='_compute_slug', store=True, unique=True)
#
#     @api.depends('title')
#     def _compute_slug(self):
#         for record in self:
#             if record.title:
#                 record.slug = self.slugify(record.title)
#
#     @staticmethod
#     def slugify(text):
#         """
#         Generate a slug from the given text.
#         """
#         text = re.sub(r'[^\w\s-]', '', text.lower())
#         return re.sub(r'\s+', '-', text).strip('-')
#
#     @api.depends('description')
#     def _compute_read_time(self):
#         for record in self:
#             if record.description:
#                 text = html2text.html2text(record.description)
#                 word_count = len(text.split())
#                 words_per_minute = 250
#                 read_time_minutes = word_count / words_per_minute
#                 record.read_time = "{}".format(max(1, round(read_time_minutes)))
#             else:
#                 record.read_time = "0"

class BlogPost(models.Model):
    _inherit = 'blog.post'

    image = fields.Binary("Image", attachment=True, help="Blog post image")