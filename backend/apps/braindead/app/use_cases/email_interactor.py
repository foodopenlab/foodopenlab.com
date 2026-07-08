from datetime import datetime

from braindead.app.dtos.email_dto import EmailResultDTO, SendEmailCommand
from braindead.app.ports.input.email_use_case import IEmailUseCase
from braindead.app.ports.output.email_port import IEmailPort
from braindead.app.ports.output.llm_port import ILLMPort


class EmailInteractor(IEmailUseCase):
    def __init__(self, email_port: IEmailPort, llm_port: ILLMPort) -> None:
        self._email_port = email_port
        self._llm_port = llm_port

    async def send_email(self, cmd: SendEmailCommand) -> EmailResultDTO:
        today = datetime.now().strftime("%Y년 %m월 %d일")
        recipient = cmd.to_name or cmd.to
        full_prompt = (
            f"오늘 날짜: {today}\n"
            f"수신자 실제 이름: {recipient} — 이메일 본문에서 반드시 이 이름을 직접 사용하세요.\n\n"
            f"규칙:\n"
            f"1. 반드시 한국어로만 작성하세요. 영어 사용 금지.\n"
            f"2. [수신자 이름], [프로젝트 이름], [연락처] 같은 대괄호 placeholder를 절대 사용하지 마세요.\n"
            f"3. 모르는 정보(전화번호, 직위 등)는 아예 쓰지 마세요.\n"
            f"4. 서명은 '감사합니다.' 한 줄로 끝내세요.\n\n"
            f"요청: {cmd.prompt}"
        )
        body_md = await self._llm_port.chat(full_prompt)
        subject = await self._llm_port.chat(
            f"다음 이메일 본문에 어울리는 제목을 한 줄로만 작성해줘. 제목 외 다른 말은 하지 마.\n\n{body_md}"
        )
        return await self._email_port.send(to=cmd.to, subject=subject, body=body_md, to_name=cmd.to_name)
