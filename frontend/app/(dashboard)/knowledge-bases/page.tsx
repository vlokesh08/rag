import { KbCreateDialog } from "@/components/knowledge-bases/kb-create-dialog"
import { KbList } from "@/components/knowledge-bases/kb-list"

export default function KnowledgeBasesPage() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Knowledge bases</h1>
        <KbCreateDialog />
      </div>
      <KbList />
    </div>
  )
}
