# -*- coding: utf-8 -*-
# from odoo import http


# class KpDeveloperLeads(http.Controller):
#     @http.route('/kp_developer_leads/kp_developer_leads', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/kp_developer_leads/kp_developer_leads/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('kp_developer_leads.listing', {
#             'root': '/kp_developer_leads/kp_developer_leads',
#             'objects': http.request.env['kp_developer_leads.kp_developer_leads'].search([]),
#         })

#     @http.route('/kp_developer_leads/kp_developer_leads/objects/<model("kp_developer_leads.kp_developer_leads"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('kp_developer_leads.object', {
#             'object': obj
#         })

