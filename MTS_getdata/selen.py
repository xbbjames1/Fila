#-*- coding:utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys




def resize_pic(s, org_size, new_size):                                                                       
    p = str(org_size)                                                                                          
    l = len(p)                                                                                                 
    n = s.rfind(p)                                                                                             
    st = s[0:n]                                                                                                
    m = st.rfind(p)                                                                                            
    new_str = s[0:m]+str(new_size)+s[m+l]+str(new_size)+s[n+l::]
    return new_str

def single_page(url):
    driver = webdriver.PhantomJS(service_args=['--load-images=no'])
    driver.get(url)
    elem = driver.find_elements_by_xpath(u'//dd/ul[contains(@data-property,"颜色")]/li')
    colors = []

    for i in elem:
        color = {}
        color['color'] = i.get_attribute('title') 
        tmp_str = i.find_element_by_tag_name('a').get_attribute('style')
        color['image_url'] = tmp_str[tmp_str.find('(')+1:tmp_str.rfind(')')]
        try:
            i.find_element_by_tag_name('a').click()
        except:
            pricings = []
        size_op = driver.find_elements_by_xpath(u'//dd/ul[contains(@data-property,"尺码")]/li')
        color['alternative_image_urls'] = None
        pricings = []
        for j in size_op:
            pricing = {}
            ch = j.find_element_by_tag_name('a').find_element_by_tag_name('span')
            pricing['size'] = ch.text
            if j.get_attribute('class')!="tb-out-of-stock":
                try:
                    j.find_element_by_tag_name('a').click()
                    in_stock = driver.find_element_by_id('J_Amount').find_element_by_id('J_EmStock')
                    pricing['inventory'] = int(in_stock.text[2:-1:])
                    pricing['in_stock'] = True
                except:
                    pricing['inventory'] = 0
                    pricing['in_stock'] = False
            else:
                pricing['in_stock'] = False
                pricing['inventory'] = 0

            org_p = driver.find_element_by_xpath('//dd/span[@class="tm-price"]')
            try:
                sale_p = driver.find_element_by_xpath('//dd/div[@class="tm-promo-price"]/span[@class="tm-price"]')
                pricing['sale_price'] = float(sale_p.text)
            except: 
                pricing['sale_price'] = float(org_p.text)
            
            pricing['currency'] = "CNY"
            pricing['original_price'] = float(org_p.text)
            pricings.append(pricing)
        
        color['image_url'] = resize_pic(color['image_url'],40,430)
        color['pricing_list'] = pricings
        colors.append(color)
    
    driver.close()
    return colors

if __name__ == '__main__':
    print single_page()
