# -*- coding: utf-8 -*-
import streamlit as st
from modules.ung_dung_khac.main import render_ung_dung_khac as module_render_ung_dung_khac

def render_ung_dung_khac(ai_engine=None):
    """
    View wrapper để gọi phân hệ Ứng dụng khác từ modules.
    Giúp tách biệt logic View và Module theo chuẩn MVC.
    """
    module_render_ung_dung_khac(ai_engine)
