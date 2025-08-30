from dataclasses import dataclass


@dataclass
class Response:
    code: int = 200
    message: str = 'success'
    data: object = None
    http_code: int = 200

    def to_json(self):
        return {
            'code': self.code,
            'message': self.message,
            'data': self.data
        }

    def to_resp(self) -> tuple[dict, int]:
        return Response.to_json(self), self.http_code