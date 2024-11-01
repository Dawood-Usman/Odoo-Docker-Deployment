# -*- coding: utf-8 -*-
# from odoo import http


# class PrEmployementOffer(http.Controller):
#     @http.route('/pr_employment_offer/pr_employment_offer', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pr_employment_offer/pr_employment_offer/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('pr_employment_offer.listing', {
#             'root': '/pr_employment_offer/pr_employment_offer',
#             'objects': http.request.env['pr_employment_offer.pr_employment_offer'].search([]),
#         })

#     @http.route('/pr_employment_offer/pr_employment_offer/objects/<model("pr_employment_offer.pr_employment_offer"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pr_employment_offer.object', {
#             'object': obj
#         })

