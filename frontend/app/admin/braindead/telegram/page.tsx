import { BraindeadTelegramForm } from "@/components/admin/braindead/telegram-form"

export default function AdminBraindeadTelegramPage() {
  return (
    <div className="container mx-auto max-w-2xl px-4 py-10">
      <div className="mb-8 space-y-3 text-center">
        <p className="text-xs font-semibold tracking-[0.24em] text-muted-foreground">BRAINDEAD · AI TELEGRAM</p>
        <h1 className="text-4xl font-black tracking-tight text-foreground sm:text-5xl">텔레그램 보내기</h1>
        <p className="mx-auto max-w-xl text-sm text-muted-foreground sm:text-base">
          내용을 설명하면 Exaone AI가 메시지를 작성하고 n8n을 통해 텔레그램으로 발송합니다.
        </p>
      </div>
      <BraindeadTelegramForm />
    </div>
  )
}
