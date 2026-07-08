import { VisionImageUploadForm } from "@/components/admin/vision/image-upload-form"

export default function AdminVisionImagesPage() {
  return (
    <div className="container mx-auto max-w-2xl px-4 py-10">
      <div className="mb-8 space-y-3 text-center">
        <p className="text-xs font-semibold tracking-[0.24em] text-muted-foreground">VISION · IMAGE UPLOAD</p>
        <h1 className="text-4xl font-black tracking-tight text-foreground sm:text-5xl">이미지 업로드</h1>
        <p className="mx-auto max-w-xl text-sm text-muted-foreground sm:text-base">
          비전 처리에 사용할 이미지를 업로드합니다. png, jpg, jpeg 등 이미지 파일만 업로드할 수 있습니다.
        </p>
      </div>
      <VisionImageUploadForm />
    </div>
  )
}
