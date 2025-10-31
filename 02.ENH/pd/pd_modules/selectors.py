"""
선택자 상수 모듈

환경 및 전제 조건:
- Windows 환경, Python 3.11.9 기준.

목적:
- PD 페이지 검증에 사용되는 CSS 선택자를 한 곳에서 관리합니다.
- 사이트 마크업 변경 시 본 파일만 수정하여 영향 범위를 최소화하는 것이 목표입니다.

사용 방법:
- 필요한 모듈에서 `from pd_modules.selectors import SELECTORS`로 임포트하여 사용합니다.
"""

# CSS 선택자 정의
SELECTORS = {
    'pd_type_container': 'div.pd-buying-price__cta',
    'standard_pd_button': 'a.cta.cta--contained.cta--emphasis.cta--2line.add-special-tagging.js-buy-now.tg-add-to-cart[an-la*="add to cart"]',
    'simple_pd_button': 'a.cta.cta--contained.cta--emphasis.cta--2line.anchorBtn[an-la*="buy now"]',
    'dimension_area': 'div.pd-sellout-option.pd-sellout-option--dimensions',
    'rating_container': 'span.pdd39-anchor-nav__info-rating',
    'rating_element': 'div.pdd39-anchor-nav__info-rating .rating',
    'price_element': 'span.pd-buying-price__new-price-currency',
    'cart_price_element': 'span.price__current.no-wrap.ng-star-inserted',
    'buying_tool_area': 'section.hdd02-buying-tool',
    'link_elements': 'section.hdd02-buying-tool a[href]',
    'start_measuring_button': 'a.cta.cta--contained.cta--black[an-la*="dimension:make sure it fits:start measuring"]',
    'dimension_popup': '.pd-sellout-option__dimensions-popup',
    'dimension_examples': 'p.text-field-v2__text.assistive',
    'dimension_inputs': 'input.text-field-v2__input',
    'fit_result': '.pd-sellout-option__dimensions-popup-result-wrap.is-show:not(.error) .pd-sellout-option__dimensions-popup-result-title',
    'not_fit_result': '.pd-sellout-option__dimensions-popup-result-wrap.is-show.error .pd-sellout-option__dimensions-popup-result-title',
    'delete_buttons': 'button.text-field-v2__input-icon.delete',
    'buy_pd_cart_button': 'a.cta.cta--contained.cta--emphasis.cta--2line.add-special-tagging.js-buy-now.tg-continue[an-la*="buy now"]',
    'cart_remove_button': 'button.cart-item__remove--btn',
    'cart_remove_confirm_modal': 'div.modal__container.cart-item-remove',
    'cart_remove_confirm_yes': 'button.pill-btn.pill-btn--blue[data-an-la="remove-item"]',
    'country_selector_modal': 'div.modal__container.country-selector-modal',
    'country_selector_checkbox': 'input.mdc-checkbox__native-control',
    'country_selector_cancel': 'button.button.pill-btn.pill-btn--white.reset.col'
}
