use crate::{arch::PAGE_SIZE, boot::RamArea};
use buddy_system_allocator::LockedHeap;
use penguin_utils::byte_size::ByteSize;

use super::page_allocator::alloc_pages;

#[global_allocator]
static ALLOCATOR: LockedHeap = LockedHeap::empty();

#[alloc_error_handler]
fn alloc_error_handler(layout: core::alloc::Layout) -> ! {
    panic!("alloc error: layout={:?}", layout);
}

pub fn init() {
    unsafe {
        let size = 1024 * 1024;
        let start = alloc_pages(size / PAGE_SIZE)
            .expect("failed to reserve memory pages for the global alllocator")
            .as_vaddr()
            .value();
        ALLOCATOR.lock().init(start, size);
    }
}

#[cfg(test)]
mod tests {
    #[test_case]
    fn alloc_crate_test() {
        use alloc::vec::Vec;
        let mut v = Vec::with_capacity(1);
        v.push('a');
        v.push('b');
        v.push('c');
        assert_eq!(v.as_slice(), &['a', 'b', 'c']);
    }
}