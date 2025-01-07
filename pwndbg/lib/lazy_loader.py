import importlib.util
import sys


lazy_modules = [
    'pwndbg.aglib',
    'pwndbg.aglib.disasm',
    'pwndbg.aglib.heap',
    'pwndbg.aglib.kernel',
    'pwndbg.gdblib.tui',
    'pwndbg.aglib.proc', # needs to be loaded early
    'pwndbg.aglib.arch',
    'pwndbg.aglib.ctypes',
    'pwndbg.aglib.disasm.aarch64',
    'pwndbg.aglib.disasm.arch',
    'pwndbg.aglib.disasm.arm',
    'pwndbg.aglib.disasm.mips',
    'pwndbg.aglib.disasm.ppc',
    'pwndbg.aglib.disasm.riscv',
    'pwndbg.aglib.disasm.sparc',
    'pwndbg.aglib.disasm.x86',
    'pwndbg.aglib.dt',
    'pwndbg.aglib.dynamic',
    'pwndbg.aglib.elf',
    'pwndbg.aglib.file',
    'pwndbg.aglib.godbg',
    'pwndbg.aglib.heap.heap',
    'pwndbg.aglib.heap.jemalloc',
    'pwndbg.aglib.heap.ptmalloc',
    'pwndbg.aglib.heap.structs',
    'pwndbg.aglib.kernel.kallsyms',
    'pwndbg.aglib.kernel.slab',
    'pwndbg.aglib.memory',
    'pwndbg.aglib.nearpc',
    'pwndbg.aglib.next',
    'pwndbg.aglib.onegadget',
    'pwndbg.aglib.qemu',
    # 'pwndbg.aglib.regs',
    'pwndbg.aglib.remote',
    'pwndbg.aglib.shellcode',
    'pwndbg.aglib.stack',
    'pwndbg.aglib.strings',
    'pwndbg.aglib.symbol',
    'pwndbg.aglib.tls',
    'pwndbg.aglib.typeinfo',
    'pwndbg.aglib.vmmap',
    'pwndbg.gdblib',
    'pwndbg.gdblib.abi',
    'pwndbg.gdblib.argv',
    'pwndbg.gdblib.bpoint',
    'pwndbg.gdblib.config',
    'pwndbg.gdblib.events',
    'pwndbg.gdblib.functions',
    'pwndbg.gdblib.got',
    'pwndbg.gdblib.hooks',
    'pwndbg.gdblib.info',
    'pwndbg.gdblib.prompt',
    'pwndbg.gdblib.ptmalloc2_tracking',
    'pwndbg.gdblib.shellcode',
    'pwndbg.gdblib.symbol',
    'pwndbg.gdblib.tui.context',
    'pwndbg.gdblib.tui.control',
    'pwndbg.gdblib.vmmap',
]


def _setup_lazy_imports(module_names):
    for module_name in module_names:
        print('name:', module_name)
        spec = importlib.util.find_spec(module_name)
        print('spec:', spec)
        loader = importlib.util.LazyLoader(spec.loader)
        spec.loader = loader
        module = importlib.util.module_from_spec(spec)

        sys.modules[module_name] = module
        loader.exec_module(module)
        parent, this_module = module_name.rsplit('.', 1)
        if parent == 'pwndbg.aglib':
            # breakpoint()
            sys.modules[parent].__dict__[this_module] = module


def lazy_load_libs():
    _setup_lazy_imports(lazy_modules)
    print('DONE!')

    import pwndbg.aglib
    import pwndbg.aglib.heap
    import pwndbg.aglib.heap.ptmalloc
    # print(type(pwndbg.aglib))
    print(sys.modules['pwndbg.aglib'].__dict__)
    print(pwndbg.aglib.__dict__)
    print(pwndbg.aglib == sys.modules['pwndbg.aglib'])
    print(sys.modules['pwndbg.aglib.heap'])
    print(pwndbg.aglib.heap)
    # breakpoint()
    print(pwndbg.aglib.heap.ptmalloc.DebugSymsHeap)
    from pwndbg.aglib.heap.ptmalloc import DebugSymsHeap
    sys.setrecursionlimit(100)
