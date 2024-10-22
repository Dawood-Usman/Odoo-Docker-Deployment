# -*- coding: utf-8 -*-
# from odoo import http


# class PrCustomHr(http.Controller):
#     @http.route('/pr_custom_hr/pr_custom_hr', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pr_custom_hr/pr_custom_hr/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('pr_custom_hr.listing', {
#             'root': '/pr_custom_hr/pr_custom_hr',
#             'objects': http.request.env['pr_custom_hr.pr_custom_hr'].search([]),
#         })

#     @http.route('/pr_custom_hr/pr_custom_hr/objects/<model("pr_custom_hr.pr_custom_hr"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pr_custom_hr.object', {
#             'object': obj
#         })

