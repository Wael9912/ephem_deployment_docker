--
-- PostgreSQL database dump
--

\restrict lfrRgOJafbK5ExklBeq4ppsWuU4EptStGlWRSy6V1cgO8iQS4hPd3PV6wlatfQb

-- Dumped from database version 16.14
-- Dumped by pg_dump version 16.14

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: backend_config; Type: TABLE DATA; Schema: public; Owner: odoo
--

INSERT INTO public.backend_config (id, create_uid, write_uid, color_pallet, drawer_color_pallet, google_font_family, appdrawer_custom_bg_color, appdrawer_custom_text_color, header_vertical_mini_text_color, header_vertical_mini_bg_color, menu_shape_bg_color, light_primary_bg_color, light_primary_text_color, dark_primary_bg_color, dark_primary_text_color, dark_secondry_bg_color, dark_secondry_text_color, dark_body_bg_color, dark_body_text_color, separator, tab, checkbox, radio, popup, chatter_position, top_menu_position, top_menu_bg_vertical_mini_2, theme_style, shape_style, font_size, loader_style, list_view_density, input_style, use_custom_colors, use_custom_drawer_color, tree_form_split_view, show_filter_row, apply_light_bg_img, apply_menu_shape_style, attachment_in_tree_view, list_view_sticky_header, create_date, write_date, menu_shape_bg_color_opacity) VALUES (1, 1, 2, 'pallet_9', 'drawer_pallet_9', NULL, '#0097a7', '#ffffff', '#2d678b', '#f9fdff', '#000000', '#0097a7', '#ffffff', '#0097a7', '#ffffff', '#242424', '#ffffff', '#1d1d1d', '#ffffff', 'separator_style_2', 'tab_style_1', 'checkbox_style_4', 'radio_style_1', 'popup_style_2', 'chatter_bottom', 'top_menu_horizontal', 'top_menu_vertical_bg1', 'biz_theme_standard', 'biz_shape_rounded', 'font_medium', 'loader_style_10', 'list_comfortable', 'input_bottom_border', false, false, NULL, NULL, false, false, false, false, '2026-06-09 16:54:43.085555', '2026-06-09 17:00:12.217871', 1);
INSERT INTO public.backend_config (id, create_uid, write_uid, color_pallet, drawer_color_pallet, google_font_family, appdrawer_custom_bg_color, appdrawer_custom_text_color, header_vertical_mini_text_color, header_vertical_mini_bg_color, menu_shape_bg_color, light_primary_bg_color, light_primary_text_color, dark_primary_bg_color, dark_primary_text_color, dark_secondry_bg_color, dark_secondry_text_color, dark_body_bg_color, dark_body_text_color, separator, tab, checkbox, radio, popup, chatter_position, top_menu_position, top_menu_bg_vertical_mini_2, theme_style, shape_style, font_size, loader_style, list_view_density, input_style, use_custom_colors, use_custom_drawer_color, tree_form_split_view, show_filter_row, apply_light_bg_img, apply_menu_shape_style, attachment_in_tree_view, list_view_sticky_header, create_date, write_date, menu_shape_bg_color_opacity) VALUES (2, 1, 1, 'pallet_19', 'drawer_pallet_19', NULL, '#0097a7', '#ffffff', '#2d678b', '#f9fdff', '#000000', '#0097a7', '#ffffff', '#0097a7', '#ffffff', '#242424', '#ffffff', '#1d1d1d', '#ffffff', 'separator_style_2', 'tab_style_1', 'checkbox_style_4', 'radio_style_1', 'popup_style_2', 'chatter_right', 'top_menu_vertical', 'top_menu_vertical_bg1', 'biz_theme_rounded', 'biz_shape_rounded', 'font_medium', 'loader_style_10', 'list_comfortable', 'input_bottom_border', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2026-06-09 23:04:48.706015', '2026-06-09 23:04:48.706015', 1);
INSERT INTO public.backend_config (id, create_uid, write_uid, color_pallet, drawer_color_pallet, google_font_family, appdrawer_custom_bg_color, appdrawer_custom_text_color, header_vertical_mini_text_color, header_vertical_mini_bg_color, menu_shape_bg_color, light_primary_bg_color, light_primary_text_color, dark_primary_bg_color, dark_primary_text_color, dark_secondry_bg_color, dark_secondry_text_color, dark_body_bg_color, dark_body_text_color, separator, tab, checkbox, radio, popup, chatter_position, top_menu_position, top_menu_bg_vertical_mini_2, theme_style, shape_style, font_size, loader_style, list_view_density, input_style, use_custom_colors, use_custom_drawer_color, tree_form_split_view, show_filter_row, apply_light_bg_img, apply_menu_shape_style, attachment_in_tree_view, list_view_sticky_header, create_date, write_date, menu_shape_bg_color_opacity) VALUES (3, 1, 1, 'pallet_19', 'drawer_pallet_19', NULL, '#0097a7', '#ffffff', '#2d678b', '#f9fdff', '#000000', '#0097a7', '#ffffff', '#0097a7', '#ffffff', '#242424', '#ffffff', '#1d1d1d', '#ffffff', 'separator_style_2', 'tab_style_1', 'checkbox_style_4', 'radio_style_1', 'popup_style_2', 'chatter_right', 'top_menu_vertical', 'top_menu_vertical_bg1', 'biz_theme_rounded', 'biz_shape_rounded', 'font_medium', 'loader_style_10', 'list_comfortable', 'input_bottom_border', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2026-06-09 23:04:48.706015', '2026-06-09 23:04:48.706015', 1);
INSERT INTO public.backend_config (id, create_uid, write_uid, color_pallet, drawer_color_pallet, google_font_family, appdrawer_custom_bg_color, appdrawer_custom_text_color, header_vertical_mini_text_color, header_vertical_mini_bg_color, menu_shape_bg_color, light_primary_bg_color, light_primary_text_color, dark_primary_bg_color, dark_primary_text_color, dark_secondry_bg_color, dark_secondry_text_color, dark_body_bg_color, dark_body_text_color, separator, tab, checkbox, radio, popup, chatter_position, top_menu_position, top_menu_bg_vertical_mini_2, theme_style, shape_style, font_size, loader_style, list_view_density, input_style, use_custom_colors, use_custom_drawer_color, tree_form_split_view, show_filter_row, apply_light_bg_img, apply_menu_shape_style, attachment_in_tree_view, list_view_sticky_header, create_date, write_date, menu_shape_bg_color_opacity) VALUES (4, 1, 1, 'pallet_19', 'drawer_pallet_19', NULL, '#0097a7', '#ffffff', '#2d678b', '#f9fdff', '#000000', '#0097a7', '#ffffff', '#0097a7', '#ffffff', '#242424', '#ffffff', '#1d1d1d', '#ffffff', 'separator_style_2', 'tab_style_1', 'checkbox_style_4', 'radio_style_1', 'popup_style_2', 'chatter_right', 'top_menu_vertical', 'top_menu_vertical_bg1', 'biz_theme_rounded', 'biz_shape_rounded', 'font_medium', 'loader_style_10', 'list_comfortable', 'input_bottom_border', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2026-06-09 23:04:48.706015', '2026-06-09 23:04:48.706015', 1);
INSERT INTO public.backend_config (id, create_uid, write_uid, color_pallet, drawer_color_pallet, google_font_family, appdrawer_custom_bg_color, appdrawer_custom_text_color, header_vertical_mini_text_color, header_vertical_mini_bg_color, menu_shape_bg_color, light_primary_bg_color, light_primary_text_color, dark_primary_bg_color, dark_primary_text_color, dark_secondry_bg_color, dark_secondry_text_color, dark_body_bg_color, dark_body_text_color, separator, tab, checkbox, radio, popup, chatter_position, top_menu_position, top_menu_bg_vertical_mini_2, theme_style, shape_style, font_size, loader_style, list_view_density, input_style, use_custom_colors, use_custom_drawer_color, tree_form_split_view, show_filter_row, apply_light_bg_img, apply_menu_shape_style, attachment_in_tree_view, list_view_sticky_header, create_date, write_date, menu_shape_bg_color_opacity) VALUES (5, 1, 1, 'pallet_19', 'drawer_pallet_19', NULL, '#0097a7', '#ffffff', '#2d678b', '#f9fdff', '#000000', '#0097a7', '#ffffff', '#0097a7', '#ffffff', '#242424', '#ffffff', '#1d1d1d', '#ffffff', 'separator_style_2', 'tab_style_1', 'checkbox_style_4', 'radio_style_1', 'popup_style_2', 'chatter_right', 'top_menu_vertical', 'top_menu_vertical_bg1', 'biz_theme_rounded', 'biz_shape_rounded', 'font_medium', 'loader_style_10', 'list_comfortable', 'input_bottom_border', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2026-06-09 23:04:48.706015', '2026-06-09 23:04:48.706015', 1);
INSERT INTO public.backend_config (id, create_uid, write_uid, color_pallet, drawer_color_pallet, google_font_family, appdrawer_custom_bg_color, appdrawer_custom_text_color, header_vertical_mini_text_color, header_vertical_mini_bg_color, menu_shape_bg_color, light_primary_bg_color, light_primary_text_color, dark_primary_bg_color, dark_primary_text_color, dark_secondry_bg_color, dark_secondry_text_color, dark_body_bg_color, dark_body_text_color, separator, tab, checkbox, radio, popup, chatter_position, top_menu_position, top_menu_bg_vertical_mini_2, theme_style, shape_style, font_size, loader_style, list_view_density, input_style, use_custom_colors, use_custom_drawer_color, tree_form_split_view, show_filter_row, apply_light_bg_img, apply_menu_shape_style, attachment_in_tree_view, list_view_sticky_header, create_date, write_date, menu_shape_bg_color_opacity) VALUES (6, 1, 1, 'pallet_19', 'drawer_pallet_19', NULL, '#0097a7', '#ffffff', '#2d678b', '#f9fdff', '#000000', '#0097a7', '#ffffff', '#0097a7', '#ffffff', '#242424', '#ffffff', '#1d1d1d', '#ffffff', 'separator_style_2', 'tab_style_1', 'checkbox_style_4', 'radio_style_1', 'popup_style_2', 'chatter_right', 'top_menu_vertical', 'top_menu_vertical_bg1', 'biz_theme_rounded', 'biz_shape_rounded', 'font_medium', 'loader_style_10', 'list_comfortable', 'input_bottom_border', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2026-06-09 23:04:48.706015', '2026-06-09 23:04:48.706015', 1);


--
-- Data for Name: google_font_family; Type: TABLE DATA; Schema: public; Owner: odoo
--

INSERT INTO public.google_font_family (id, config_id, user_id, create_uid, write_uid, name, url, is_selected, create_date, write_date) VALUES (1, 1, 2, NULL, NULL, 'Alexandria', 'https://fonts.google.com/specimen/Alexandria?query=alexandria', true, '2026-06-09 16:58:09.336751', '2026-06-09 16:58:09.336751');


--
-- Name: backend_config_id_seq; Type: SEQUENCE SET; Schema: public; Owner: odoo
--

SELECT pg_catalog.setval('public.backend_config_id_seq', 6, true);


--
-- Name: google_font_family_id_seq; Type: SEQUENCE SET; Schema: public; Owner: odoo
--

SELECT pg_catalog.setval('public.google_font_family_id_seq', 1, true);


--
-- PostgreSQL database dump complete
--

\unrestrict lfrRgOJafbK5ExklBeq4ppsWuU4EptStGlWRSy6V1cgO8iQS4hPd3PV6wlatfQb

