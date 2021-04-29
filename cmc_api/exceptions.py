class CMCAPIException(Exception):
    pass


class BadRequestException(Exception):
    pass


class UnauthorizedException(Exception):
    pass


class PaymentRequiredException(Exception):
    pass


class ForbiddenException(Exception):
    pass


class TooManyRequestsException(Exception):
    pass


class InternalServerErrorException(Exception):
    pass
