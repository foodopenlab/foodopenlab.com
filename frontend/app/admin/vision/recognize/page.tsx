import { FaceRecognizeForm } from "@/components/admin/vision/face-recognize-form"

export default function AdminVisionRecognizePage() {
  return (
    <div className="container mx-auto max-w-2xl px-4 py-10">
      <div className="mb-8 space-y-3 text-center">
        <p className="text-xs font-semibold tracking-[0.24em] text-muted-foreground">VISION · FACE RECOGNITION</p>
        <h1 className="text-4xl font-black tracking-tight text-foreground sm:text-5xl">객체 탐지</h1>
        <p className="mx-auto max-w-xl text-sm text-muted-foreground sm:text-base">
          사람 얼굴 이미지를 올리면 학습된 YOLO 모델이 누구인지 예측합니다.
        </p>
      </div>
      <FaceRecognizeForm />
    </div>
  )
}
