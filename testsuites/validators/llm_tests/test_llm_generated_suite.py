from validators import (
    between,
    card_number,
    visa,
    mastercard,
    amex,
    unionpay,
    diners,
    jcb,
    discover,
    mir,
    calling_code,
    country_code,
    currency,
    cron,
    bsc_address,
    btc_address,
    eth_address,
    trx_address,
    domain,
    email,
    base16,
    base32,
    base58,
    base64,
    cusip,
    isin,
    sedol,
    md5,
    sha1,
    sha224,
    sha256,
    sha384,
    sha512,
    hostname,
    fi_business_id,
    fi_ssn,
    es_cif,
    es_doi,
    es_nie,
    es_nif,
    fr_department,
    fr_ssn,
    ind_aadhar,
    ind_pan,
    ru_inn,
    iban,
    ipv4,
    ipv6,
    length,
    mac_address,
    slug,
    url,
    uuid,
)

def test_between():
    assert between(5, min_val=2) is True
    assert between(5, max_val=10) is True
    assert not (between(5, min_val=6))
    assert not (between(5, max_val=4))
    assert between(5, min_val=None, max_val=None) is True

def test_card_number():
    assert card_number('4242424242424242') is True
    assert not (card_number('4242424242424241'))
    assert not (card_number(''))
    assert card_number('5555555555554444') is True

def test_visa():
    assert visa('4242424242424242') is True
    assert not (visa('2223003122003222'))

def test_mastercard():
    assert mastercard('5555555555554444') is True
    assert not (mastercard('4242424242424242'))

def test_amex():
    assert amex('378282246310005') is True
    assert not (amex('4242424242424242'))

def test_unionpay():
    assert unionpay('6200000000000005') is True
    assert not (unionpay('4242424242424242'))

def test_diners():
    assert diners('3056930009020004') is True
    assert not (diners('4242424242424242'))

def test_jcb():
    assert jcb('3566002020360505') is True
    assert not (jcb('4242424242424242'))

def test_discover():
    assert discover('6011111111111117') is True
    assert not (discover('4242424242424242'))

def test_mir():
    assert mir('2200123456789019') is True
    assert not (mir('4242424242424242'))

def test_calling_code():
    assert calling_code('+91') is True
    assert not (calling_code('-31'))

def test_country_code():
    assert country_code('GB', iso_format='alpha2') is True
    assert country_code('USA') is True
    assert country_code('840', iso_format='numeric') is True
    assert not (country_code('iN', iso_format='alpha2'))

def test_currency():
    assert currency('USD') is True
    assert not (currency('INVALID'))

def test_cron():
    assert cron('*/5 * * * *') is True
    assert not (cron('30-20 * * * *'))

def test_bsc_address():
    assert bsc_address('0x4e5acf9684652BEa56F2f01b7101a225Ee33d23f') is True
    assert not (bsc_address('0x4g5acf9684652BEa56F2f01b7101a225Eh33d23z'))

def test_btc_address():
    assert btc_address('3Cwgr2g7vsi1bXDUkpEnVoRLA9w4FZfC69') is True
    assert not (btc_address('1BvBMsEYstWetqTFn5Au4m4GFg7xJaNVN2'))

def test_eth_address():
    assert eth_address('0x9cc14ba4f9f68ca159ea4ebf2c292a808aaeb598') is True
    assert not (eth_address('0x8Ba1f109551bD432803012645Ac136ddd64DBa72'))

def test_trx_address():
    assert trx_address('TLjfbTbpZYDQ4EoA4N5CLNgGjfbF8ZWz38') is True
    assert not (trx_address('TR2G7Rm4vFqF8EpY4U5xdLdQ7XgJ2U8Vd'))

def test_domain():
    assert domain('example.com') is True
    assert not (domain('example.com/'))

def test_email():
    assert email('someone@example.com') is True
    assert not (email('bogus@@'))

def test_base16():
    assert base16('a3f4b2') is True
    assert not (base16('a3f4Z1'))

def test_base32():
    assert base32('MFZWIZLTOQ======') is True
    assert not (base32('MfZW3zLT9Q======'))

def test_base58():
    assert base58('14pq6y9H2DLGahPsM4s7ugsNSD2uxpHsJx') is True
    assert base58('cUSECm5YzcXJwP') is True

def test_base64():
    assert base64('Y2hhcmFjdGVyIHNldA==') is True
    assert not (base64('cUSECm5YzcXJwP'))

def test_cusip():
    assert cusip('037833DP2') is True
    assert not (cusip('037833DP3'))

def test_isin():
    assert isin('US0378331005') is True
    assert not (isin('US037833100'))

def test_sedol():
    assert sedol('2936921') is True
    assert not (sedol('29A6922'))

def test_md5():
    assert md5('d41d8cd98f00b204e9800998ecf8427e') is True
    assert not (md5('900zz11'))

def test_sha1():
    assert sha1('da39a3ee5e6b4b0d3255bfef95601890afd80709') is True
    assert not (sha1('900zz11'))

def test_sha224():
    assert sha224('d14a028c2a3a2bc9476102bb288234c415a2b01f828ea62ac5b3e42f') is True
    assert not (sha224('900zz11'))

def test_sha256():
    assert sha256('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855') is True
    assert not (sha256('900zz11'))

def test_sha384():
    assert sha384('cb00753f45a35e8bb5a03d699ac65007272c32ab0eded1631a8b605a43ff5bed8086072ba1e7cc2358baeca134c825a7') is True
    assert not (sha384('900zz11'))

def test_sha512():
    assert sha512('cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e') is True
    assert not (sha512('900zz11'))

def test_hostname():
    assert hostname('ubuntu-pc:443') is True
    assert hostname('this-pc') is True
    assert hostname('xn----gtbspbbmkef.xn--p1ai:65535') is True
    assert not (hostname('_example.com'))

def test_fi_business_id():
    assert fi_business_id('0112038-9') is True
    assert not (fi_business_id('1234567-8'))

def test_fi_ssn():
    assert fi_ssn('010101-0101') is True
    assert not (fi_ssn('101010-0102'))

def test_es_cif():
    assert es_cif('B25162520') is True
    assert not (es_cif('B25162529'))

def test_es_nif():
    assert es_nif('26643189N') is True
    assert not (es_nif('26643189X'))

def test_fr_department():
    assert not (fr_department(20))
    assert not (fr_department("20"))
    assert fr_department("971") is True
    assert not (fr_department("00"))
    assert fr_department('2A') is True
    assert fr_department('2B') is True
    assert not (fr_department('2C'))

def test_fr_ssn():
    assert fr_ssn('1 84 12 76 451 089 46') is True
    assert fr_ssn('1 84 12 76 451 089') is True
    assert not (fr_ssn('3 84 12 76 451 089 46'))
    assert not (fr_ssn('1 84 12 76 451 089 47'))

def test_ind_aadhar():
    assert ind_aadhar('3675 9834 6015') is True
    assert not (ind_aadhar('3675 ABVC 2133'))

def test_ind_pan():
    assert ind_pan('ABCDE9999K') is True
    assert not (ind_pan('ABC5d7896B'))

def test_ru_inn():
    assert ru_inn('500100732259') is True
    assert ru_inn('7830002293') is True
    assert not (ru_inn('1234567890'))

def test_iban():
    assert iban('DE29100500001061045672') is True
    assert not (iban('123456'))

def test_ipv4():
    assert ipv4('123.0.0.7') is True
    assert ipv4('1.1.1.1/8') is True
    assert not (ipv4('900.80.70.11'))

def test_ipv6():
    assert ipv6('::ffff:192.0.2.128') is True
    assert ipv6('::1/128') is True
    assert not (ipv6('abc.0.0.1'))

def test_length():
    assert length('something', min_val=2) is True
    assert length('something', min_val=9, max_val=9) is True
    assert not (length('something', max_val=5))

def test_mac_address():
    assert mac_address('01:23:45:67:ab:CD') is True
    assert not (mac_address('00:00:00:00:00'))

def test_slug():
    assert slug('my-slug-2134') is True
    assert not (slug('my.slug'))

def test_url():
    assert url('http://duck.com') is True
    assert url('ftp://foobar.dk') is True
    assert url('http://10.0.0.1') is True
    assert not (url('http://example.com/">user@example.com'))

def test_uuid():
    assert uuid('2bc1c94f-0deb-43e9-92a1-4775189ec9f8') is True
    assert not (uuid('2bc1c94f 0deb-43e9-92a1-4775189ec9f8'))
