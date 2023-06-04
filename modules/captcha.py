import tls_client


class Captcha_Manager:
    '''
    This class uses paid services to solve hCaptcha

    [capmonster] -> HCaptchaTask
    [capsolver] -> Soon
    [anti-captcha] -> Soon
    '''

    def __init__(self, api_key: str):
        self.client = tls_client.Session(
            client_identifier="chrome112",
            random_tls_extension_order=True
        )

        self.api_key = api_key


    def solver(self, rqdata):
        '''
        
        '''
