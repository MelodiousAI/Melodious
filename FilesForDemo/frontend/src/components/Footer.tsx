export function Footer() {
  return (
    <footer className="mt-20 border-t border-border py-10">
      <div className="container mx-auto px-6 text-center">
        <p className="font-sans text-sm text-muted-foreground">
          (c) {new Date().getFullYear()} Melodious - Sheet music, understood.
        </p>
      </div>
    </footer>
  )
}
